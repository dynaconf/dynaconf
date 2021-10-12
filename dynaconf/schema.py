from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional

from .validator import ValidationError
from .validator import Validator
from dynaconf.utils.functional import empty


class SchemaError(Exception):
    ...


class Field:
    def __init__(
        self,
        default: Optional[Any] = empty,
        validators: Optional[List[Validator]] = None,
    ):
        self.default = default
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
        return cls(**kwargs)  # type: ignore

    @classmethod
    def validate(cls, settings) -> None:
        data = settings.as_dict(exclude=["dynaconf_schema", "load_dotenv"])
        instance = cls._create(**data)
        fields = instance.__dataclass_fields__.items()  # type: ignore
        for name, field in fields:

            value = getattr(
                instance, name, getattr(instance, name.swapcase(), None)
            )

            dynaconf_validators = []
            if isinstance(field.default, Field):
                if value is field.default:
                    value = value.default
                dynaconf_validators = field.default.validators

            if value is empty:
                raise SchemaError(
                    f"Missing required field `{name}`` in `{cls.__name__}`. "
                    f"Please check your settings files, environment, "
                    f"or privide a default value, "
                    f"`{name}: {field.type.__name__} = Field(default, ...)` "
                    f"if the field is not required you can set it to None "
                    f"`{name}: {field.type.__name__} = None`"
                )

            try:
                field.type(value)
            except ValueError:
                raise SchemaError(
                    f"Invalid type for {name} "
                    f"expected `{field.type.__name__}` "
                    f"got `{type(value).__name__}`"
                )

            if name not in settings:
                settings.set(name, value)

            for validator in dynaconf_validators:
                validator.names = (name,)
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
