import enum
import inspect
import typing
from dataclasses import _MISSING_TYPE
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import get_origin
from typing import List
from typing import Optional
from typing import Tuple

from .validator import ValidationError
from .validator import Validator
from dynaconf.utils.functional import empty
from dynaconf.utils.parse_conf import jinja_env
from dynaconf.vendor.jinja2.exceptions import UndefinedError


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

    @classmethod
    def config(cls, settings=None) -> SchemaConfig:
        custom_config = {
            k: v
            for k, v in vars(cls.Config).items()
            if k in SchemaConfig.__dataclass_fields__  # type: ignore
        }
        return SchemaConfig(**custom_config)

    @classmethod
    def should_skip_set(
        cls,
        key,
        loader_identifier=None,
    ) -> bool:
        """Return True if the key must be filtered out
        this method is called on Dynaconf.set()
        """
        # being set by the schema so always allow
        # or coming from envvar so we allow to never break by external
        # interference on environment.
        if loader_identifier in ("schema_default",):
            return False

        # Try to get field from schema case insensitive
        # key, Key, KEY, kEY, KEy, KEy, keY will match
        dc_field = cls.allowed_fields().get(
            key,
            cls.allowed_fields().get(
                cls.normalized_allowed_keys().get(key.lower(), key.upper()),
            ),
        )

        # Field is part of the schema, but being set by a loader
        # does user wants default from schema forced?
        if dc_field and getattr(dc_field.default, "force_default", False):
            return True

        # Value comming from loaders
        # key is not defined on schema
        # does user wants to ignore or allow this value?
        if cls.config().extra_fields_policy == ExtraFields.ignore:
            return dc_field is None

        if cls.config().extra_fields_policy == ExtraFields.forbid:
            # Do not raise when there is a key in env var but raise for
            # other sources.
            if dc_field is None:
                if loader_identifier == "env_global":
                    return True
                raise SchemaError(
                    f"Extra field '{key}' is not allowed in schema"
                )

        # extra_fields_policy is allow
        return False

    @classmethod
    def allowed_fields(cls, settings=None) -> Dict[str, Any]:
        return cls.__dataclass_fields__  # type: ignore

    # @classmethod
    # def known_long_names(cls, parent: str=None) -> List[str]:
    #     names = []
    #     normalized_allowed_keys = cls.normalized_allowed_keys()
    #     for dc_name, dc_field in cls.allowed_fields().items():
    #         name = normalized_allowed_keys.get(dc_name, dc_name)
    #         if issubclass(dc_field.type, Schema):
    #             names.extend(dc_field.type.known_long_names(name))
    #         long_name = [parent, name] if parent else [name]
    #         names.append("__".join(long_name).lower())
    #     return names

    @classmethod
    def normalized_allowed_keys(cls) -> Dict[str, str]:
        # a lower only list pointing to schema defined fields
        # {"mykey": "MyKey"}
        # So we know which key to set independent of case
        normalized_allowed_keys = {
            k.lower(): k for k in cls.allowed_fields().keys()
        }
        return normalized_allowed_keys

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
        normalized_allowed_keys = cls.normalized_allowed_keys()

        for key, value in d.items():
            if key in allowed_keys:  # already there, nothing to do
                new_d[key] = value
            else:  # can be a case of case mismatch lets find a match
                key = normalized_allowed_keys.get(key.lower(), key)

            if key in new_d:
                # if isinstance(value, (list, tuple)):
                #     new_d[key] += value
                if isinstance(value, dict):
                    new_d[key].update(value)
                else:
                    new_d[key] = value
            else:
                new_d[key] = value

        return new_d

    @classmethod
    def _get_default_value(cls, field: Field, settings: Any) -> Any:
        """Get the default value for a field."""
        if field.default_expr:
            try:
                return jinja_env.compile_expression(field.default_expr)(
                    this=settings,
                    settings=settings,
                    schema=cls,
                )
            except UndefinedError as e:
                raise SchemaError(
                    f"default_expr failed: {e} "
                    f"HINT: Check the order of field definition in "
                    f"`{cls.__name__}`, "
                    f"`{field.name}` field must go after the fields used in "
                    f"default_expr: '{field.default_expr}'"
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
                default_kwargs["schema"] = cls
            try:
                return field.default_factory(**default_kwargs)
            except AttributeError as e:
                raise SchemaError(
                    f"default_factory failed: {e} "
                    f"HINT: Check the order of field definition in "
                    f"`{cls.__name__}`, "
                    f"`{field.name}` field must go after the fields used in "
                    f"default_factory: '{field.default_factory}'"
                )
        return field.default

    @classmethod
    def validate(
        cls, settings, subschema_data: dict = None, parent_name: str = None
    ) -> Tuple[Optional[Dict[str, Any]], List]:
        """Validate settings based on the schema.

        1. Get the data to validade, if root object it is settings as dict,
           if it is a compund object then it is the passed in subschema_data.
        2. Adjust the key case to match the schema fields.
           because dynaconf allows UPPER and lowercase keys.
        3. depending on the extra_fields_policy, filter the data to:
           `ignore|allow`: filter out extra fields from validation.
           `forbid`: keep extra fields to raise an error on instantiation.
        4. Iterate over the schema fields to perform:
           - custom validators accumulation
           - default value assignment or calculation
           - Schema type cast validation
             - if the type is a SubSchema, then recursively validate it.
        5. Attemp to instantiate the object.
        6. Custom validators
        7. Return the validated data.
        """
        custom_validators = []  # to accumulate from schema iteration
        final_data = {}  # to accumulate from schema iteration

        # value coming from settings loader or subschema data
        loaded_data = subschema_data or settings.as_dict(
            exclude=["dynaconf_schema"]
        )
        loaded_data = cls.adjust_key_case(loaded_data)

        for dc_name, dc_field in cls.allowed_fields().items():
            # build the dotted name ex: "my_schema.name.name"
            long_name = cls.get_long_name(parent_name, dc_name)

            # Get the value from the schema if set
            value = dc_field.default
            force_default = getattr(value, "force_default", False)

            if isinstance(value, Field):
                # If there are validators, then accumulate them
                if value.validators:
                    custom_validators.extend(
                        cls.build_named_validators(value.validators, long_name)
                    )

                # Then we see if the value must be overridden by
                # `default` or `default_factory` or `default_expr`
                if dc_name not in loaded_data or force_default:
                    value = cls._get_default_value(value, settings=settings)
                elif dc_name in loaded_data:
                    value = loaded_data[dc_name]

                # If schema does't provide a default and it is not loaded
                if value is empty:
                    cls.raise_for_missing(long_name, dc_field)

            elif isinstance(value, _MISSING_TYPE):
                # If the value is missing ex: dataclass has only `key:type`
                # then we see if it is
                # defined in the loaded data
                if dc_name in loaded_data:
                    value = loaded_data[dc_name]
                else:
                    cls.raise_for_missing(long_name, dc_field)

            # Schema type cast validation
            value, validators = cls.validate_field_type(
                settings, parent_name, dc_name, dc_field, long_name, value
            )
            custom_validators.extend(validators)

            # Reaching this line means we have the final value to set.
            final_data[dc_name] = value

            if not subschema_data and (
                dc_name not in settings or force_default
            ):
                settings.set(
                    dc_name, value, loader_identifier="schema_default"
                )

        # if cls.config().extra_fields_policy == "forbid":
        #     # No extra fields is allowed on loaded settings
        #     if extra := set(loaded_data.keys()) - set(final_data.keys()):
        #         raise SchemaError(
        #             f"Extra fields {extra} are not allowed on "
        #             f"{cls.__name__} because extra_fields_policy = 'forbid' "
        #             f"to allow extra fields change it to 'allow' or "
        #             f"'ignore' to ignore extra fields."
        #         )

        if not parent_name:
            cls.run_dynaconf_validators(custom_validators, settings=settings)

        return final_data, custom_validators

    @classmethod
    def raise_for_missing(cls, dc_name, dc_field):
        raise SchemaError(
            f"Missing `{dc_name}` in `{cls.__name__}`. "
            f"check your settings files, environment variables "
            f"or provide a default value, `{dc_name}"
            f": {dc_field.type.__name__} = Field(default)` "
            f"if field is not required set it to None "
            f"`{dc_name}: {dc_field.type.__name__} = None`"
        )

    @classmethod
    def validate_field_type(
        cls, settings, parent_name, dc_name, dc_field, long_name, value
    ) -> Tuple[Any, List]:
        validators = []

        try:
            if issubclass(dc_field.type, Schema) and isinstance(value, dict):
                value, validators = dc_field.type.validate(
                    settings,
                    subschema_data=value,
                    parent_name=long_name,
                )
                if parent_name is None:
                    settings.set(
                        long_name, value, loader_identifier="schema_default"
                    )
            else:
                dc_field.type(value)
        except (TypeError, ValueError) as e:
            # NOTE: Find a way to evaluate typing at runtime here
            special_type = dc_field.type.__class__ in (
                typing._SpecialForm,
                typing._GenericAlias,  # type: ignore
            )
            if not special_type and get_origin(dc_field.type) is None:
                raise SchemaError(
                    f"Invalid type for `{cls.__name__}.{long_name}` "
                    f"expected `{dc_field.type.__name__}` "
                    f"got `{type(value).__name__}` "
                    f"error: {e}"
                )

        return value, validators

    @classmethod
    def get_long_name(cls, parent_name: Optional[str], dc_name: str) -> str:
        _names = [parent_name] if parent_name else []
        long_name = ".".join(_names + [dc_name])
        return long_name

    @classmethod
    def build_named_validators(
        cls, validators: List[Any], long_name: str
    ) -> List[Validator]:
        accumulation = []
        for validator in validators:
            if isinstance(validator, Validator):
                validator.names = (long_name,)
                validator.must_exist = True
            elif isinstance(validator, str):
                validator = Validator(long_name, expr=validator, required=True)
            elif callable(validator):
                validator = Validator(
                    long_name, condition=validator, required=True
                )
            else:
                raise SchemaError(
                    f"Invalid validator type: {type(validator).__name__}"
                )
            accumulation.append(validator)
        return accumulation

    @classmethod
    def run_dynaconf_validators(
        cls, validators: List[Validator], settings: Any
    ):
        for validator in validators:
            try:
                validator.validate(settings)
            except ValidationError as e:
                raise SchemaError(str(e))
