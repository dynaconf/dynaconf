import enum
import inspect
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from .validator import ValidationError
from .validator import Validator
from dynaconf.utils.functional import empty
from dynaconf.utils.parse_conf import jinja_env


class SchemaError(Exception):
    ...


class ExtraFields(str, enum.Enum):
    allow = "allow"  # Load from settings even if not in schema
    forbid = "forbid"  # Raise error if not in schema but found in settings
    ignore = "ignore"  # Do not load from settings if not on schema


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

    @classmethod
    @property
    def config(cls) -> SchemaConfig:
        custom_config = {
            k: v
            for k, v in vars(cls.Config).items()
            if k in SchemaConfig.__dataclass_fields__  # type: ignore
        }
        return SchemaConfig(**custom_config)

    @classmethod
    @property
    def allowed_fields(cls) -> Dict[str, Any]:
        return cls.__dataclass_fields__  # type: ignore

    @classmethod
    def filter_dict(cls, d: dict) -> dict:
        """Filter the dict to only keep the schema fields.

        Args:
            d: dict to filter

        Returns:
            dict: filtered dict
        """
        allowed_keys = cls.allowed_fields
        return {
            k: v
            for k, v in d.items()
            if k in allowed_keys  # type: ignore
            or k.swapcase() in allowed_keys  # type: ignore
            or k.upper().endswith("FOR_DYNACONF")  # Dynaconf internal config
        }

    @classmethod
    def _create(cls, **kwargs) -> "Schema":
        for key in list(kwargs.keys()):
            if not any([key.isupper(), key.islower()]):
                raise ValueError(
                    f"Invalid key {key} in schema. "
                    "keys must be lowercase or UPPERCASE."
                )
            if not hasattr(cls, key):
                kwargs[key.swapcase()] = kwargs.pop(key)

        if cls.config.extra_fields_policy != "forbid":  # type: ignore
            kwargs = cls.filter_dict(kwargs)

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
    def validate(cls, settings) -> None:
        data = settings.as_dict(exclude=["dynaconf_schema"])
        instance = cls._create(**data)
        fields = cls.__dataclass_fields__.items()  # type: ignore
        for dc_name, dc_field in fields:
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
                if instance_value is field or force_default:
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

            try:
                dc_field.type(value)
            except TypeError as e:
                # NOTE: implement type validator here
                pass
            except ValueError:
                raise SchemaError(
                    f"Invalid type for {dc_name} "
                    f"expected `{dc_field.type.__name__}` "
                    f"got `{type(value).__name__}`"
                )

            if dc_name not in settings or force_default:
                settings.set(
                    dc_name, value, loader_identifier="schema_default"
                )

            for validator in getattr(field, "validators", []):

                if isinstance(validator, Validator):
                    validator.names = (dc_name,)
                elif isinstance(validator, str):
                    validator = Validator(dc_name, expr=validator)
                elif callable(validator):
                    validator = Validator(dc_name, condition=validator)

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
        if schema := self.schemas.get(settings.current_env):
            schema.validate(settings)
