"""Implements wrappers, types and helpers for Schema based settings."""

from __future__ import annotations  # WARNING: remove this when debugging

from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import cast

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
            new_cls.validators.validate()

        return cast(cls, new_cls)


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

    # NOTE: move to inspect.get_annotations when Python 3.9 is dropped
    if isinstance(schema_cls, type):
        schema_annotations = schema_cls.__dict__.get("__annotations__", {})
    else:
        schema_annotations = getattr(schema_cls, "__annotations__", {})

    for name, _annotation in schema_annotations.items():
        default_value = getattr(schema_cls, name, empty)
        full_path = path + (name,)  # E.g, ("path", "to", "name")
        full_name = ".".join(full_path)  # E.g, path.to.name
        # take the type from Annotated[type, *metadata]
        _type = getattr(_annotation, "__origin__", None)
        _type_args = getattr(_annotation, "__args__", None)
        # take the metadata from Annotated[type, *metadata]
        _annotated_validators = getattr(_annotation, "__metadata__", None)

        if default_value is not empty:
            defaults[full_name] = default_value

        if isinstance(_annotation, type) and issubclass(_annotation, Nested):
            defaults, validators = extract_defaults_and_validators_from_typing(
                _annotation, full_path, defaults, validators
            )
        elif _annotated_validators:
            for _validator in _annotated_validators:
                _validator.names = [full_name]
                if _type:
                    _validator.is_type_of = _type
                if default_value is empty:
                    _validator.must_exist = True  # required
                validators.append(_validator)
        else:
            if _type_args and _type in (list, tuple):
                _validator = Validator(full_name, is_type_of=_type)
                enc_type = _type_args[0]
                enclosed_defaults, enclosed_validators = (
                    extract_defaults_and_validators_from_typing(enc_type)
                )
                if enclosed_defaults:
                    raise DynaconfSchemaError(
                        "List enclosed types cannot define default values. "
                        f"{enc_type.__name__!r} defines {enclosed_defaults}. "
                        f"this is error is caused by "
                        f"`{full_name}: {_type.__name__}[{enc_type.__name__}]`"
                    )
                # Transform the lis tof enclosed_validators in a function
                # that will be added as _validator.condition
                # that function will iterate the items in the list
                # and ensure each validator validates.
                if enclosed_validators:
                    _validator.condition = (
                        lambda value: validate_enclosed_list(
                            value, enclosed_validators, full_name
                        )
                    )
            else:
                _validator = Validator(full_name, is_type_of=_annotation)

            if default_value is empty:
                _validator.must_exist = True  # required
            validators.append(_validator)

    return defaults, validators


def validate_enclosed_list(values, validators, prefix):
    """takes list[_type] and test against validators"""
    for value in values:
        for validator in validators:
            msgs = {
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
            validator.messages.update(msgs)
            validator.validate(BaseDynaconfSettings(**value))
    # No validation error
    return True
