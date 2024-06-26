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
from .types import _NotRequiredMarker
from .types import DictValue
from .types import SUPPORTED_TYPES


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
    # These names passes down recursively
    path = path or tuple()
    defaults = defaults or {}
    validators = validators or []

    for name, annotation in get_annotations(schema_cls).items():
        if name == "dynaconf_options":
            # In case someone does dyanconf_options: Options = Options(...)
            # That value is kept out of the schema validation
            continue

        default_value = getattr(schema_cls, name, empty)
        full_path = path + (name,)  # E.g, ("path", "to", "name")
        full_name = ".".join(full_path)  # E.g, path.to.name
        _type, _type_args, _args_validators = get_type_and_args(annotation)
        raise_for_unsupported_type(full_name, _type, _type_args, annotation)
        is_notrequired = False

        if _args_validators and isinstance(
            _args_validators[0], _NotRequiredMarker
        ):
            # Annotated[NotRequired[T], ...]
            _, *_args_validators = _args_validators
            is_notrequired = True
        if _args_validators and isinstance(
            _args_validators[-1], _NotRequiredMarker
        ):
            # NotRequired[Annotated[T, ...]]
            *_args_validators, _ = _args_validators
            is_notrequired = True

        if default_value is not empty:
            previous_default = defaults.get(".".join(path))
            already_defined = (
                isinstance(previous_default, dict) and name in previous_default
            )
            if not already_defined:
                defaults[full_name] = default_value

        raise_for_optional_without_none(
            full_name, _type, _type_args, default_value, annotation
        )

        # field: DictValue
        if is_dict_value(annotation):
            validators.append(BaseValidator(full_name, is_type_of=dict))
            # Recursively call this same function until all nested exhausts.
            defaults, validators = extract_defaults_and_validators_from_typing(
                annotation, full_path, defaults, validators
            )
        # field: Annotated[T, Validator(...)]
        elif _args_validators:
            raise_for_invalid_annotated(full_name, _type, _args_validators)

            for _validator in _args_validators:
                _validator.names = (full_name,)
                _validator.is_type_of = _type
                if default_value is empty and not is_notrequired:
                    _validator.must_exist = True
                validators.append(_validator)

        # field: list[T]
        elif is_enclosed_list(_type, _type_args):
            _validator = BaseValidator(full_name, is_type_of=_type)
            inner_type, *more_types = _type_args

            # NOT SURE ABOUT THIS
            raise_for_invalid_amount_of_enclosed_types(
                full_name, _type, inner_type, more_types
            )

            enclosed_defaults, enclosed_validators = (
                extract_defaults_and_validators_from_typing(inner_type)
            )

            raise_for_enclosed_with_defaults(
                full_name, _type, inner_type, enclosed_defaults, annotation
            )

            _validator.condition = validator_condition_factory(
                enclosed_validators, full_name, inner_type
            )

            if default_value is empty and not is_notrequired:
                _validator.must_exist = True  # required

            validators.append(_validator)
        # field: T
        else:
            _validator = BaseValidator(full_name)
            if default_value is empty and not is_notrequired:
                _validator.must_exist = True  # required

            if is_notrequired:
                # Extract the types from the Annotated
                if is_dict_value(annotation):
                    _validator.is_type_of = dict
                else:
                    _validator.is_type_of = _type
            else:
                _validator.is_type_of = annotation

            validators.append(_validator)

    return defaults, validators


def get_all_enclosed_types(inner_type):
    # # Handle list[Union...]
    if is_union(inner_type):
        all_types = get_args(inner_type)
    else:
        all_types = (inner_type,)
    return all_types


def get_type_name(_type):
    if name := getattr(_type, "__name__", None):
        return name
    return str(_type)


def get_type_and_args(annotation) -> tuple:
    """From annotation name: T[T, args] extract type, args, validators."""
    _annotated_validators = None
    _type_args: tuple = tuple()
    # _type from `field: T` or `field: list[T]`
    _type = get_origin(annotation) or annotation
    if _type is Annotated:
        _type, *_annotated_validators = get_args(annotation)
    else:
        _type_args = get_args(annotation)
    return _type, _type_args, _annotated_validators


def is_dict_value(annotation):
    return isinstance(annotation, type) and issubclass(annotation, DictValue)


def is_enclosed_list(_type, _type_args):
    return _type_args and _type in (list, tuple)


def is_union(annotation) -> bool:
    """Tell if an annotation is strictly Union."""
    return get_origin(annotation) is Union


def is_optional(annotation) -> bool:
    """Tell if an annotation is strictly typing.Optional or Union[**, None]"""
    return is_union(annotation) and type(None) in get_args(annotation)


def is_type(value) -> bool:
    _type = get_origin(value) or value
    return isinstance(_type, type) or is_union(value) or is_optional(value)


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


def raise_for_invalid_annotated(full_name, _type, _args_validators) -> None:
    if isinstance(_type, type) and issubclass(_type, DictValue):
        raise DynaconfSchemaError(
            f"{get_type_name(_type)!r} type cannot be Annotated, "
            f"set the validators on the {get_type_name(_type)!r} fields "
            f"this error is caused by "
            f"`{full_name}: Annotated[{get_type_name(_type)!r}, *]`"
        )
    if not all(isinstance(arg, BaseValidator) for arg in _args_validators):
        raise DynaconfSchemaError(
            f"Invalid Annotated Args "
            f"all items must be instances of Validator "
            f"this error is caused by "
            f"`{full_name}: Annotated[{get_type_name(_type)!r}"
            f"[{', '.join(str(i) for i in _args_validators)}]`"
        )


def raise_for_invalid_amount_of_enclosed_types(
    full_name, _type, inner_type, more_types
) -> None:
    """Decided to consider only the first enclosed type
    which means list[T] is allowed, but list[T, T] not
    This is subject to change in future.
    """
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


def raise_for_enclosed_with_defaults(
    full_name, _type, inner_type, enclosed_defaults, annotation
):
    """A DictValue enclosed on list[DictValue] cannot define defaults.
    because it is indexed and we have no way to return default values from
    dynaconf.get.
    """
    if enclosed_defaults:
        raise DynaconfSchemaError(
            "List enclosed types cannot define default values. "
            f"{inner_type.__name__!r} defines {enclosed_defaults}. "
            f"this error is caused by "
            f"`{full_name}: {_type.__name__}[{inner_type.__name__}]`"
        )


def raise_for_unsupported_type(
    full_name, _type, _type_args, annotation
) -> None:
    _types = _type_args or [_type]
    for _type in _types:
        _type_origin = get_origin(_type) or _type
        _type_args = get_args(_type)
        if _type_args:  # Union[] or list[] or tuple[]
            raise_for_unsupported_type(
                full_name, _type, _type_args, annotation
            )
        unsupported = isinstance(_type, type) and not issubclass(
            _type_origin, SUPPORTED_TYPES
        )
        if unsupported:
            raise DynaconfSchemaError(
                f"Invalid type {get_type_name(_type)!r} "
                f"must be one of {SUPPORTED_TYPES} "
                f"this error is caused by "
                f"`{full_name}: {annotation}`"
            )


def raise_for_optional_without_none(
    full_name, _type, _type_args, default_value, annotation
):
    if default_value is empty and is_optional(annotation):
        raise DynaconfSchemaError(
            f"Optional Union "
            "must assign `None` explicitly as default. "
            f"try changing to: `{full_name}: {annotation} = None` "
            f"this error is caused by "
            f"`{full_name}: {annotation}`. "
            "Did you mean to declare as `NotRequired` "
            f"instead of {get_type_name(annotation)!r}?"
        )


def raise_for_invalid_class_variable(cls):
    """typed.Dynaconf only allows typed variables or dynaconf_options attr"""
    for name, value in vars(cls).items():
        if (
            name.startswith(("_", "dynaconf_options"))
            or name in cls.__annotations__
        ):
            continue
        msg = (
            f"Invalid assignment on `{get_type_name(cls)}:"
            f" {name} = {get_type_name(value)}`. "
            "All attributes must include type annotations or "
            "be a `dynaconf_options = Options(...)`. "
        )
        if is_type(value):
            msg += f"Did you mean '{name}: {get_type_name(value)}'?"
        else:
            msg += f"Did you mean '{name}: T = {value}'?"

        raise DynaconfSchemaError(msg)
