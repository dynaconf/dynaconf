from __future__ import annotations  # WARNING: remove this when debugging

from typing import Annotated
from typing import Callable
from typing import get_args
from typing import get_origin
from typing import Union

from dynaconf.base import Settings as BaseDynaconfSettings
from dynaconf.utils.functional import empty
from dynaconf.validator import Validator as BaseValidator

from .compat import get_annotations
from .exceptions import DynaconfSchemaError
from .types import DictValue

# Types that can be used on `field: list[x]`
ALLOWED_ENCLOSED_TYPES = (
    DictValue,
    int,
    float,
    str,
    bool,
    type(None),
    list,
    tuple,
    dict,
)


def extract_defaults_and_validators_from_typing(
    schema_cls,
    path: tuple | None = None,
    defaults: dict | None = None,
    validators: list | None = None,
) -> tuple[dict, list]:
    """From schema class extract defaults and validators from annotations.

    Recursively handle all `DictValue` subtypes.

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

        _type, _type_args, _args_validators = get_type_and_args(annotation)

        if default_value is not empty:
            previous_default = defaults.get(".".join(path))
            already_defined = (
                isinstance(previous_default, dict) and name in previous_default
            )
            if not already_defined:
                defaults[full_name] = default_value

        # it is a field: DictValue
        if isinstance(annotation, type) and issubclass(annotation, DictValue):
            defaults, validators = extract_defaults_and_validators_from_typing(
                annotation, full_path, defaults, validators
            )
        # It is a field: Annotated[type, Validator(...)]
        elif _args_validators:
            if isinstance(_type, type) and issubclass(_type, DictValue):
                raise DynaconfSchemaError(
                    "DictValue type cannot be Annotated, "
                    f"set the validators on the {_type.__name__!r} fields "
                    f"this error is caused by "
                    f"`{full_name}: Annotated[{_type.__name__}, *]`"
                )

            for _validator in _args_validators:
                _validator.names = (full_name,)
                _validator.is_type_of = _type
                if default_value is empty and not is_optional(annotation):
                    _validator.must_exist = True  # required
                validators.append(_validator)

        # it is a field: list[DictValue] (or any ALLOWED_ENCLOSED_TYPES)
        elif _type_args and _type in (list, tuple):
            _validator = BaseValidator(full_name, is_type_of=_type)
            # ADR: Decided to consider only the first enclosed type
            # which means T[T] is allowed, but T[T, T] not
            # This is subject to change in future, PRs welcome.
            inner_type, *more_types = _type_args
            if more_types:
                raise DynaconfSchemaError(
                    f"Invalid enclosed type for {full_name} "
                    "enclosed types supports only one argument "
                    f"{get_type_name(_type)}[{get_type_name(inner_type)}] "
                    "is allowed, but this error is caused by "
                    f"`{full_name}: {get_type_name(_type)}"
                    f"[{get_type_name(inner_type)}, "
                    f"{', '.join(get_type_name(i) for i in more_types)}]`"
                )

            # # Handle list[Union...]
            if is_union(inner_type):
                all_types = get_args(inner_type)
            else:
                all_types = (inner_type,)

            for item in all_types:
                if not issubclass(item, ALLOWED_ENCLOSED_TYPES):
                    raise DynaconfSchemaError(
                        f"Invalid enclosed type {get_type_name(item)!r} "
                        f"must be one of {ALLOWED_ENCLOSED_TYPES} "
                        f"this error is caused by "
                        f"`{full_name}: {get_type_name(_type)}"
                        f"[{get_type_name(inner_type)}]`"
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

            _validator.condition = validator_condition_factory(
                enclosed_validators, full_name, inner_type
            )

            if default_value is empty and not is_optional(annotation):
                _validator.must_exist = True  # required

            validators.append(_validator)

        # It is just a bare type annotation like field: type
        else:
            _validator = BaseValidator(full_name, is_type_of=annotation)
            if default_value is empty and not is_optional(annotation):
                _validator.must_exist = True  # required
            validators.append(_validator)

    return defaults, validators


def get_type_name(_type):
    if name := getattr(_type, "__name__", None):
        return name
    return str(_type)


def get_type_and_args(annotation) -> tuple:
    """From annotation name: T[T, args] extract type, args, validators"""
    _annotated_validators = None
    _type_args: tuple = tuple()
    _type = get_origin(annotation)  # type from X[type,]
    if _type is Annotated:
        _type, *_annotated_validators = get_args(annotation)
    else:
        _type_args = get_args(annotation)
    return _type, _type_args, _annotated_validators


def is_union(annotation) -> bool:
    """Tell if an annotation is strictly Union."""
    return get_origin(annotation) is Union


def is_optional(annotation) -> bool:
    """Tell if an annotation is strictly typing.Optional or Union[**, None]"""
    return is_union(annotation) and type(None) in get_args(annotation)


def validator_condition_factory(validators, prefix, _type) -> Callable:
    """takes _type: T, generates a function to validate a value against it"""

    def validator_condition(values):
        if isinstance(_type, type) and issubclass(_type, DictValue):  # a dict
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
                "condition": (
                    "{name}[] invalid for {function}({value}) in env {env}"
                ),
                "operations": (
                    "{name}[] must {operation} {op_value} "
                    "but it is {value} in env {env}"
                ),
            }
            for value in values:
                _settings = BaseDynaconfSettings()
                _settings.set(prefix, value)
                _validator = BaseValidator(
                    prefix,
                    is_type_of=_type,
                    messages=validator_messages,
                )
                _validator.validate(_settings)

        # No validation error
        return True

    return validator_condition
