# pragma: no cover
"""
Implement basic assertions to be used in assertion action
"""

from __future__ import annotations

from typing import get_args
from typing import get_origin
from typing import Union

# NOTE: Remove when dropping 3.9
try:
    from types import UnionType  # type: ignore
except ImportError:
    UnionType = Union  # type: ignore
# /NOTE


def eq(value, other):
    """Equal"""
    return value == other


def ne(value, other):
    """Not equal"""
    return value != other


def gt(value, other):
    """Greater than"""
    return value > other


def lt(value, other):
    """Lower than"""
    return value < other


def gte(value, other):
    """Greater than or equal"""
    return value >= other


def lte(value, other):
    """Lower than or equal"""
    return value <= other


def identity(value, other):
    """Identity check using ID"""
    return value is other


def is_type_of(value, other):
    """Type check that performs lookup on parameterized generic types.
    For singular primary types this check is very fast ans just
    calls isinstance.
    For SpecialForm annotations like Union and Parametrized types like T[T]
    or T[T, T] then this is a bit more costly.
    NOTE: Find ways to improve the execution time on this, like
    caching same value -> same type
    """

    origin = get_origin(other)
    args = get_args(other)

    if not args and isinstance(other, tuple):
        # Got (T[T],) from recursive call
        return any(is_type_of(value, item) for item in other)

    if args:
        if origin in [Union, UnionType]:
            return any(is_type_of(value, arg) for arg in args)
        elif origin in (list, tuple):
            return isinstance(value, (list, tuple)) and all(
                is_type_of(item, args) for item in value
            )
        elif origin is dict:
            k_type, v_type = args
            return isinstance(value, dict) and all(
                is_type_of(k, k_type) and is_type_of(v, v_type)
                for k, v in value.items()
            )

    if getattr(other, "_dynaconf_dictvalue", None):
        other = dict

    return isinstance(value, other)


def is_in(value, other):
    """Existence"""
    return value in other


def is_not_in(value, other):
    """Inexistence"""
    return value not in other


def cont(value, other):
    """Contains"""
    return other in value


def len_eq(value, other):
    """Length Equal"""
    return len(value) == other


def len_ne(value, other):
    """Length Not equal"""
    return len(value) != other


def len_min(value, other):
    """Minimum length"""
    return len(value) >= other


def len_max(value, other):
    """Maximum length"""
    return len(value) <= other


def startswith(value, term):
    """returns value.startswith(term) result"""
    return value.startswith(term)


def endswith(value, term):
    """returns value.endswith(term) result"""
    return value.endswith(term)
