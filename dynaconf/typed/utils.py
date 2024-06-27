from __future__ import annotations  # WARNING: remove this when debugging

from typing import Annotated
from typing import Callable
from typing import get_args
from typing import get_origin
from typing import Union

from dynaconf.base import Settings as BaseDynaconfSettings
from dynaconf.validator import Validator as BaseValidator

from .compat import UnionType
from .types import DictValue


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
    return get_origin(annotation) in [Union, UnionType]


def is_optional(annotation) -> bool:
    """Tell if an annotation is strictly typing.Optional or Union[**, None]"""
    return is_union(annotation) and type(None) in get_args(annotation)


def is_type(value) -> bool:
    _type = get_origin(value) or value
    return isinstance(_type, type) or is_union(value) or is_optional(value)


def validator_condition_factory(validators, prefix, _type) -> Callable:
    """takes _type: T, generates a function to validate a value against it"""

    # _type_origin = get_origin(_type) or _type
    # print(_type, _type_origin)
    # _type_origin = get_origin(_type)
    def validator_condition(values):
        if isinstance(_type, type) and issubclass(_type, DictValue):
            for i, value in enumerate(values):
                for _validator in validators:
                    for k, v in _validator.messages.items():
                        _validator.messages[k] = v.replace(
                            "{name}", prefix + f"[{i}]." + "{name}"
                        )
                    _validator.validate(BaseDynaconfSettings(**value))
        else:
            for i, value in enumerate(values):
                _settings = BaseDynaconfSettings()
                _settings.set(prefix, value)
                _validator = BaseValidator(
                    prefix,
                    is_type_of=_type,
                )
                for k, v in _validator.messages.items():
                    _validator.messages[k] = v.replace(
                        "{name}", "{name}" + f"[{i}]"
                    )
                _validator.validate(_settings)

        # No validation error
        return True

    return validator_condition
