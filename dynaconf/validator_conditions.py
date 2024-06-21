# pragma: no cover
"""
Implement basic assertions to be used in assertion action
"""

from __future__ import annotations

from typing import get_args
from typing import get_origin
from typing import Union


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
    """Type check"""
    # Support Union[T, Y, Z] for python 3.9
    # on python 3.10 isinstance can handle Union
    if get_origin(other) is Union:
        other = get_args(other)
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
