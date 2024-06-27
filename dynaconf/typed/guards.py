from dynaconf.utils.functional import empty
from dynaconf.validator import Validator as BaseValidator

from . import exceptions as ex
from . import types as ty
from . import utils as ut


def raise_for_invalid_annotated(full_name, _type, _args_validators) -> None:
    if not all(isinstance(arg, BaseValidator) for arg in _args_validators):
        raise ex.DynaconfSchemaError(
            f"Invalid Annotated Args "
            f"all items must be instances of Validator "
            f"this error is caused by "
            f"`{full_name}: Annotated[{ut.get_type_name(_type)!r}"
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
        raise ex.DynaconfSchemaError(
            f"Invalid enclosed type for {full_name} "
            "enclosed types supports only one argument "
            f"{ut.get_type_name(_type)}[{ut.get_type_name(inner_type)}] "
            "is allowed, but this error is caused by "
            f"`{full_name}: {ut.get_type_name(_type)}"
            f"[{ut.get_type_name(inner_type)}, "
            f"{', '.join(ut.get_type_name(i) for i in more_types)}]`"
        )


def raise_for_enclosed_with_defaults(
    full_name, _type, inner_type, enclosed_defaults, annotation
):
    """A DictValue enclosed on list[DictValue] cannot define defaults.
    because it is indexed and we have no way to return default values from
    dynaconf.get.
    """
    if enclosed_defaults:
        raise ex.DynaconfSchemaError(
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
        _type_origin = ut.get_origin(_type) or _type
        _type_args = ut.get_args(_type)
        if _type_args:  # Union[] or list[] or tuple[]
            raise_for_unsupported_type(
                full_name, _type, _type_args, annotation
            )
        unsupported = isinstance(_type, type) and not issubclass(
            _type_origin, ty.SUPPORTED_TYPES
        )
        if unsupported:
            raise ex.DynaconfSchemaError(
                f"Invalid type {ut.get_type_name(_type)!r} "
                f"must be one of {ty.SUPPORTED_TYPES} "
                f"this error is caused by "
                f"`{full_name}: {annotation}`"
            )


def raise_for_optional_without_none(
    full_name, _type, _type_args, default_value, annotation
):
    if default_value is empty and ut.is_optional(annotation):
        raise ex.DynaconfSchemaError(
            f"Optional Union "
            "must assign `None` explicitly as default. "
            f"try changing to: `{full_name}: {annotation} = None` "
            f"this error is caused by "
            f"`{full_name}: {annotation}`. "
            "Did you mean to declare as `NotRequired` "
            f"instead of {ut.get_type_name(annotation)!r}?"
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
            f"Invalid assignment on `{ut.get_type_name(cls)}:"
            f" {name} = {ut.get_type_name(value)}`. "
            "All attributes must include type annotations or "
            "be a `dynaconf_options = Options(...)`. "
        )
        if ut.is_type(value):
            msg += f"Did you mean '{name}: {ut.get_type_name(value)}'?"
        else:
            msg += f"Did you mean '{name}: T = {value}'?"

        raise ex.DynaconfSchemaError(msg)
