"""Implements wrappers, types and helpers for Schema based settings."""

from __future__ import annotations  # WARNING: remove this when debugging

from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from typing import get_args
from typing import get_origin
from typing import Union

from dynaconf.base import LazySettings as OriginalDynaconf
from dynaconf.base import Settings as BaseDynaconfSettings
from dynaconf.validator import ValidationError  # noqa
from dynaconf.validator import Validator


class Empty: ...


empty = Empty()


@dataclass  # wanted to pass (kw_only=True) but that works only for 3.10+
class Options:
    """Options to configure the initialization of Dynaconf Object.

    NOTE: This must be used only with typed implementation of Dynaconf.

    All options are just bypassed to the Dynaconf `__init__` method,
    except those starting with `_`.

    Options starting with `_` are only used on `__new__` when building the
    new Dynaconf object, those values assumes opinionated defaults and rarely
    needs to be changed.
    """

    # NOTE: On a dataclass the sentinel must be a Type not an instance

    env: str | type = Empty
    environments: bool | type = Empty
    envvar_prefix: str | type = Empty
    root_path: str | Path | type = Empty
    settings_files: list[str] | type = Empty
    settings_file: str | type = Empty

    _trigger_validation: bool = True

    def as_dict(self):
        options_dict = asdict(self)
        options_dict = {
            k: v
            for k, v in options_dict.items()
            if (not k.startswith("_")) and v is not Empty
        }
        return options_dict


class DynaconfSchemaError(Exception): ...


class Nested: ...


class Dynaconf(BaseDynaconfSettings, Nested):
    """Implementation of Dynaconf that is aware of type annotations."""

    def __new__(cls, *args, **kwargs):
        options = getattr(cls, "dynaconf_options", Options())
        defaults, validators = extract_defaults_and_validators_from_typing(cls)
        passed_in_validators = kwargs.pop("validators", [])
        validators += passed_in_validators

        # Set init options for Dynaconf coming first from Options on Schema
        init_options = options.as_dict()
        # Add defaults defined on class as it was passed to Dynaconf(k=v)
        init_options.update(defaults)
        # Override from kwargs as if matching key was passed to Settings(k=v)
        init_options.update(kwargs)

        # Instantiate the new Dynaconf instance
        new_cls = OriginalDynaconf(*args, **init_options)
        new_cls.__annotations__ = cls.__annotations__

        if validators:
            new_cls.validators.register(*validators)

        # Trigger validation if not explicitly disabled
        if options._trigger_validation:
            new_cls.validators.validate_all()

        return cast(cls, new_cls)


def is_union(annotation) -> bool:
    """Tell if an annotation is strictly Union."""
    return get_origin(annotation) is Union


def is_optional(annotation) -> bool:
    """Tell if an annotation is strictly typing.Optional or Union[**, None]"""
    return is_union(annotation) and type(None) in get_args(annotation)


def get_annotated_metadata(annotation) -> tuple | None:
    """metadata from Annotated[type, *metadata]"""
    # Any other way to extract metadata from Annotated?
    if "Annotated" in str(annotation):
        return getattr(annotation, "__metadata__", None)
    return None


# Types that can be used on `field: list[x]`
ALLOWED_ENCLOSED_TYPES = (
    Nested,
    int,
    float,
    str,
    bool,
    type(None),
    list,
    tuple,
    dict,
)


def get_annotations(schema_cls) -> dict:
    """NOTE: move to inspect.get_annotations when Python 3.9 is dropped"""
    if isinstance(schema_cls, type):
        return schema_cls.__dict__.get("__annotations__", {})
    else:
        return getattr(schema_cls, "__annotations__", {})


def extract_defaults_and_validators_from_typing(
    schema_cls,
    path: tuple | None = None,
    defaults: dict | None = None,
    validators: list | None = None,
) -> tuple[dict, list]:
    """From schema class extract defaults and validators from annotations.

    Recursively handle all `Nested` subtypes.

    key: int -> Validator(key, is_type_of=int)
    key: int = 1 -> Validator(key, is_type_of=int) + defaults[key] = 1
    key: Annotated[int, Validator()] -> Validator(key, is_type_of=int)
    """
    path = path or tuple()
    defaults = defaults or {}
    validators = validators or []
    schema_annotations = get_annotations(schema_cls)

    for name, annotation in schema_annotations.items():
        default_value = getattr(schema_cls, name, empty)
        full_path = path + (name,)  # E.g, ("path", "to", "name")
        full_name = ".".join(full_path)  # E.g, path.to.name

        # NOTE: get_origin doesn't work for Annotated
        # _type = get_origin(annotation)  # type from X[type,]
        _type = getattr(annotation, "__origin__", None)

        # In case of Annotated, the following will return (T, *metadata)
        _type_args = get_args(annotation)  # args from X[_,*args]

        if default_value is not empty:
            defaults[full_name] = default_value

        # it is a field: Nested
        if isinstance(annotation, type) and issubclass(annotation, Nested):
            defaults, validators = extract_defaults_and_validators_from_typing(
                annotation, full_path, defaults, validators
            )
        # It is a field: Annotated[type, Validator(...)]
        elif _annotated_validators := get_annotated_metadata(annotation):
            if isinstance(_type, type) and issubclass(_type, Nested):
                raise DynaconfSchemaError(
                    "Nested type cannot be Annotated, "
                    f"set the validators on the {_type.__name__!r} fields "
                    f"this error is caused by "
                    f"`{full_name}: Annotated[{_type.__name__}, *]`"
                )

            for _validator in _annotated_validators:
                _validator.names = [full_name]
                _validator.is_type_of = _type
                if default_value is empty and not is_optional(annotation):
                    _validator.must_exist = True  # required
                validators.append(_validator)

        # it is a field: list[Nested] (or any ALLOWED_ENCLOSED_TYPES)
        elif _type_args and _type in (list, tuple):
            _validator = Validator(full_name, is_type_of=_type)
            # consider only the first by now, should it handle more?
            inner_type = _type_args[0]
            if not issubclass(inner_type, ALLOWED_ENCLOSED_TYPES):
                raise DynaconfSchemaError(
                    f"Invalid enclosed type {inner_type.__name__!r} "
                    f"must be one of {ALLOWED_ENCLOSED_TYPES} "
                    f"this error is caused by "
                    f"`{full_name}: {_type.__name__}[{inner_type.__name__}]`"
                )

            enclosed_defaults, enclosed_validators = (
                extract_defaults_and_validators_from_typing(inner_type)
            )
            if enclosed_defaults:
                raise DynaconfSchemaError(
                    "List enclosed types cannot define default values. "
                    f"{inner_type.__name__!r} defines {enclosed_defaults}. "
                    f"this error is caused by "
                    f"`{full_name}: {_type.__name__}[{inner_type.__name__}]`"
                )

            _validator.condition = validate_enclosed_list(
                enclosed_validators, full_name, inner_type
            )

            if default_value is empty and not is_optional(annotation):
                _validator.must_exist = True  # required

            validators.append(_validator)

        # It is just a bare type annotation like field: type
        else:
            _validator = Validator(full_name, is_type_of=annotation)
            if default_value is empty and not is_optional(annotation):
                _validator.must_exist = True  # required
            validators.append(_validator)

    return defaults, validators


def validate_enclosed_list(validators, prefix, _type):
    """takes list[_type] and test against validators"""

    def validator_condition(values):
        if issubclass(_type, Nested):  # a dict
            validator_messages = {
                "must_exist_true": prefix
                + "[].{name} is required in env {env}",
                "must_exist_false": prefix
                + "[].{name} cannot exists in env {env}",
                "condition": prefix
                + "[].{name} invalid for {function}({value}) in env {env}",
                "operations": (
                    prefix + "[].{name} must {operation} {op_value} "
                    "but it is {value} in env {env}"
                ),
            }
            for value in values:
                for validator in validators:
                    validator.messages.update(validator_messages)
                    validator.validate(BaseDynaconfSettings(**value))
        else:  # not a dict
            validator_messages = {
                "must_exist_true": "{name}[] is required in env {env}",
                "must_exist_false": "{name}[] cannot exists in env {env}",
                "condition": "{name}[] invalid for {function}({value}) in env {env}",
                "operations": (
                    "{name}[] must {operation} {op_value} "
                    "but it is {value} in env {env}"
                ),
            }
            for value in values:
                _settings = BaseDynaconfSettings()
                _settings.set(prefix, value)
                _validator = Validator(
                    prefix,
                    is_type_of=_type,
                    messages=validator_messages,
                )
                _validator.validate(_settings)

        # No validation error
        return True

    return validator_condition
