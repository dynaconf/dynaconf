import enum
import inspect
import typing
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import get_origin
from typing import List
from typing import Optional

from .validator import ValidationError
from .validator import Validator
from dynaconf import default_settings
from dynaconf.utils.functional import empty
from dynaconf.utils.parse_conf import jinja_env


class SchemaError(Exception):
    ...


class ExtraFields(str, enum.Enum):
    allow = "allow"  # Load from settings even if not in schema
    forbid = "forbid"  # Raise error if not in schema but found in settings
    ignore = "ignore"  # Do not load from settings if not on schema


class SchemaValidationMode(str, enum.Enum):
    eager = "eager"  # trigger loading and validation as soon as possible
    lazy = "lazy"  # trigger loading and validation only fist access


class Field:
    def __init__(
        self,
        default: Optional[Any] = empty,
        default_factory: Optional[Callable] = None,
        default_expr: Optional[str] = None,
        force_default: bool = False,
        validators: Optional[List[Validator]] = None,
    ):

        if default_expr is not None and default_factory is not None:
            raise SchemaError(
                "You can't use both default_expr and default_factory"
            )

        if default is not empty and any((default_expr, default_factory)):
            raise SchemaError(
                "You can't define default with default_expr or default_factory"
            )

        self.default = default
        self.default_factory = default_factory
        self.default_expr = default_expr
        self.force_default = force_default
        self.validators = validators or []

    def __set_name__(self, owner: Any, name: str):
        self.name = name

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: Any):
        instance.__dict__[self.name] = value


@dataclass
class SchemaConfig:
    extra_fields_policy: ExtraFields = ExtraFields.allow
    validation_mode: SchemaValidationMode = SchemaValidationMode.eager


@dataclass
class Schema:
    """A Schema to define settings and validate them.

    Usage:
        >>> from dynaconf import Schema, Field
        >>> class MySchema(Schema):
        ...     name: str = Field()
        ...     age: int = Field()
        >>> from dynaconf import Dynaconf
        >>> dynaconf = Dynaconf(
        ...     settings_file="my_settings.yaml",
        ...     dynaconf_schema=MySchema
        ... )

    Dynaconf will use the MySchema class to validate the settings file:
        >>> MySchema.validate(settings)

    No one is allowed to instantiate a Schema object directly.
    """

    class Config:
        ...

    @classmethod  # cant be a property because of Python 3.8
    def config(cls, settings=None) -> SchemaConfig:
        custom_config = {
            k: v
            for k, v in vars(cls.Config).items()
            if k in SchemaConfig.__dataclass_fields__  # type: ignore
        }
        return SchemaConfig(**custom_config)

    @classmethod  # cant be a property because of Python 3.8
    def allowed_fields(cls, settings=None) -> Dict[str, Any]:
        return cls.__dataclass_fields__  # type: ignore

    @classmethod
    def filter_dict(cls, d: dict, settings=None) -> dict:
        """Filter the dict to only keep the schema fields.

        Args:
            d: dict to filter

        Returns:
            dict: filtered dict
        """
        allowed_keys = cls.allowed_fields()
        return {
            k: v
            for k, v in d.items()
            if k in allowed_keys  # type: ignore
            or k.swapcase() in allowed_keys  # type: ignore
            or k.upper().endswith("FOR_DYNACONF")  # Dynaconf internal config
        }

    @classmethod
    def adjust_key_case(cls, d: dict) -> dict:
        """Adjust the key case of the dict to match the schema fields.

        Args:
            d: dict to adjust

        Returns:
            dict: adjusted dict
        """
        new_d = {}
        allowed_keys = cls.allowed_fields()
        for key, value in d.items():
            if key in allowed_keys:  # nothing to do
                new_d[key] = value
            elif not any([key.isupper(), key.islower()]):  # invalid for adjust
                raise SchemaError(
                    f"Invalid key {key} in schema. "
                    "keys must be lowercase or UPPERCASE."
                )
            elif key.swapcase() in allowed_keys:  # inverse case is present
                new_d[key.swapcase()] = value
            else:
                new_d[key] = value  # key is extra_field
        return new_d

    @classmethod
    def _create(cls, **kwargs) -> "Schema":
        try:
            return cls(**kwargs)  # type: ignore
        except TypeError as e:
            raise SchemaError(e)

    @classmethod
    def _get_default_value(
        cls, field: Field, settings: Any, schema: "Schema"
    ) -> Any:
        """Get the default value for a field."""
        if field.default_expr:
            return jinja_env.compile_expression(field.default_expr)(
                this=settings,
                settings=settings,
                schema=schema,
            )
        elif field.default_factory:
            default_kwargs = {}
            default_params = inspect.signature(
                field.default_factory
            ).parameters
            if "this" in default_params:
                default_kwargs["this"] = settings
            elif "settings" in default_params:
                default_kwargs["settings"] = settings
            elif "st" in default_params:
                default_kwargs["st"] = settings
            if "schema" in default_params:
                default_kwargs["schema"] = schema
            return field.default_factory(**default_kwargs)
        return field.default

    @classmethod
    def validate(
        cls, settings, subschema_data: dict = None, parent_name: str = None
    ) -> Optional[Dict]:
        """Validate settings based on the schema.

        1. Get the data to validade, if root object it is settings as dict,
           if it is a compund object then it is the passed in subschema_data.
        2. Adjust the key case to match the schema fields.
           because dynaconf allows UPPER and lowercase keys.
        3. depending on the extra_fields_policy, filter the data to:
           `ignore|allow`: filter out extra fields from validation.
           `forbid`: keep extra fields and raise an error on instantiation.
        """
        # 1
        data = subschema_data or settings.as_dict(exclude=["dynaconf_schema"])
        # 2
        data = cls.adjust_key_case(data)
        # 3
        if cls.config().extra_fields_policy != "forbid":  # type: ignore
            data = cls.filter_dict(data)

        instance = cls._create(**data)
        fields = cls.__dataclass_fields__.items()  # type: ignore
        for dc_name, dc_field in fields:
            long_name = cls.get_long_name(parent_name, dc_name)
            field = dc_field.default  # _MISSING_TYPE or Field
            force_default = getattr(field, "force_default", False)

            instance_value = getattr(
                instance, dc_name, getattr(instance, dc_name.swapcase(), None)
            )

            # by default value takes the value defined
            # on dataclass or loaded from settings
            value = instance_value

            # if the field is an instance of our Field class
            if isinstance(field, Field):
                # Then we see if the value must be overridden by `default` args
                if value is field or force_default:
                    value = cls._get_default_value(
                        field,
                        settings=settings,
                        schema=instance,
                    )

            if value is empty:
                raise SchemaError(
                    f"Missing required field `{dc_name}`` in `{cls.__name__}`."
                    f" Please check your settings files, environment, "
                    f" or privide a default value, "
                    f"`{dc_name}: {dc_field.type.__name__} = Field(default)` "
                    f"if the field is not required you can set it to None "
                    f"`{dc_name}: {dc_field.type.__name__} = None`"
                )

            value = cls.validate_field_type(
                settings, parent_name, dc_name, dc_field, long_name, value
            )

            if not subschema_data and (
                dc_name not in settings or force_default
            ):
                settings.set(
                    dc_name, value, loader_identifier="schema_default"
                )

            # if subschema_data:
            #     subschema_data = cls.adjust_key_case(subschema_data)
            #     if dc_name not in subschema_data or force_default:
            #         # NOTE: handle upper/lower case
            #         # PROBLEM: HERE
            #         debug(dc_name)
            #         debug(subschema_data)
            #         subschema_data[dc_name] = value

            cls.run_dynaconf_validators(settings, long_name, field)

        return subschema_data

    @classmethod
    def validate_field_type(
        cls, settings, parent_name, dc_name, dc_field, long_name, value
    ) -> Any:
        try:
            if issubclass(dc_field.type, Schema) and isinstance(value, dict):
                value = dc_field.type.validate(
                    settings,
                    subschema_data=value,
                    parent_name=long_name,
                )
                if parent_name is None:
                    # NOTE: upper/lower, force default?
                    settings.set(
                        dc_name, value, loader_identifier="schema_default"
                    )
            else:
                dc_field.type(value)
        except (TypeError, ValueError) as e:
            # NOTE: Find a way to evaluate typing at runtime here
            # debug(e)
            special_type = dc_field.type.__class__ in (
                typing._SpecialForm,
                typing._GenericAlias,  # type: ignore
            )
            if not special_type and get_origin(dc_field.type) is None:
                raise SchemaError(
                    f"Invalid type for `{cls.__name__}.{dc_name}` "
                    f"expected `{dc_field.type.__name__}` "
                    f"got `{type(value).__name__}` "
                    f"error: {e}"
                )

        return value

    @classmethod
    def get_long_name(cls, parent_name: Optional[str], dc_name: str) -> str:
        _names = [parent_name] if parent_name else []
        long_name = ".".join(_names + [dc_name])
        return long_name

    @classmethod
    def run_dynaconf_validators(cls, settings, long_name, field):
        for validator in getattr(field, "validators", []):
            if isinstance(validator, Validator):
                validator.names = (long_name,)
            elif isinstance(validator, str):
                validator = Validator(long_name, expr=validator)
            elif callable(validator):
                validator = Validator(long_name, condition=validator)

            try:
                validator.validate(settings)
            except ValidationError as e:
                raise SchemaError(str(e))


class SchemaEnvHolder:
    """A class to hold multiple schemas to be validated on environments

    Usage:
        >>> from dynaconf import SchemaEnvHolder, Schema, Field, Dynaconf
        >>> class MySchema(Schema):
        ...     name: str = Field()
        ...     age: int = Field()
        >>> settings = Dynaconf(
        ...     schema=SchemaEnvHolder(production=MySchema)
        ... )
    """

    def __init__(self, /, **kwargs):
        self.schemas = kwargs

    def validate(self, settings) -> None:
        if schema := self.schemas.get(settings.current_env.lower()):
            schema.validate(settings)

    def config(self, settings=None) -> SchemaConfig:
        try:
            return self.schemas.get(settings.current_env.lower()).config()
        except AttributeError:
            return self.schemas.get(
                default_settings.ENV_FOR_DYNACONF.lower()
            ).config()

    def allowed_fields(self, settings=None) -> Dict[str, Any]:
        try:
            return self.schemas.get(
                settings.current_env.lower()
            ).allowed_fields()
        except AttributeError:
            return self.schemas.get(
                default_settings.ENV_FOR_DYNACONF.lower()
            ).allowed_fields()
