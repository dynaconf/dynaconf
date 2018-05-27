# coding: utf-8
# pragma: no cover
"""
Implement basic assertions to be used in assertion action
"""


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
    return isinstance(value, other)


def is_in(value, other):
    """Existence"""
    return value in other


def is_not_in(value, other):
    """Inexistence"""
    return value not in other
