from __future__ import annotations  # WARNING: remove this when debugging

from collections.abc import Sequence
from typing import Annotated
from typing import Any
from typing import Callable
from typing import TypeVar
from typing import Union

from dynaconf.utils.functional import Empty
from dynaconf.utils.functional import empty
from dynaconf.validator import Validator as BaseValidator

from .compat import get_annotations

T = TypeVar("T")


class NotRequiredMarker:
    __slots__ = ()


NotRequired = Annotated[T, NotRequiredMarker()]
"""
This type will mark keys as NotRequired which means it can be completely
absent from the settings object.
This differs from Optional, as Optional requires T or None,
NotRequired requires T or simply nothing at all.
In practice this will make the generated Validator to have required=False
and skip the check for a default value, so settings.key will raise for
AttributeError.

When used as `NotRequired[T]`
    _type = T, _type_args = (_NotRequiredMarker(),)
When uses as `Annotated[NotRequired[T], Validator()]`
    _type = T
    _type_args (_NotRequiredMarker(), Validator())

"""


class DictValue:
    """DictValue represents a Typed Dict in the settings.

    When instantiating just returns a dict containing the default values only,
    this type does not performs any validation.
    """

    __slots__ = ()
    _dynaconf_dictvalue = True  # a marker for validator_conditions.is_type_of

    def __new__(cls, **kwargs):
        defaults = {}
        schema_annotations = get_annotations(cls)
        for name, annotation in schema_annotations.items():
            value = getattr(cls, name, empty)
            if value is not empty:
                defaults[name] = value
        defaults.update(kwargs)
        return defaults


class Validator:
    """Define an interface to generate a valid BaseValidator.

    The `operations` are::

        eq: value == other
        ne: value != other
        gt: value > other
        lt: value < other
        gte: value >= other
        lte: value <= other
        is_type_of: isinstance(value, type)
        is_in:  value in sequence
        is_not_in: value not in sequence
        identity: value is other
        cont: contain value in
        len_eq: len(value) == other
        len_ne: len(value) != other
        len_min: len(value) > other
        len_max: len(value) < other
        startswith: value.startswith(term)
        endswith:  value.endswith(term)
        condition: fn(value) is True


    """

    __slots__ = ()

    def __new__(
        cls,
        *,  # kw_only
        # Operations
        eq: Any = empty,
        ne: Any = empty,
        gt: Any = empty,
        lt: Any = empty,
        gte: Any = empty,
        lte: Any = empty,
        identity: Any = empty,
        is_in: Any = empty,
        is_not_in: Any = empty,
        cont: Any = empty,
        len_eq: Any = empty,
        len_ne: Any = empty,
        len_min: Any = empty,
        len_max: Any = empty,
        startswith: Any = empty,
        endswith: Any = empty,
        condition: Callable[[Any], bool] | None | Empty = empty,
        # options
        env: str | Sequence[str] | None | Empty = empty,
        messages: dict[str, str] | None | Empty = empty,
        cast: Callable[[Any], Any] | None | Empty = empty,
        description: str | None | Empty = empty,
        items_validators: list[BaseValidator] | None = None,
        # To be implemented, a interface like this to generate a When Validator
        # when: When | None = empty,
    ):
        kwargs = locals()
        kwargs.pop("cls")
        return BaseValidator(
            **{k: v for k, v in kwargs.items() if v is not empty}
        )


class ItemsValidator:
    """Interface to instantiate a new Validator with items_validators"""

    __slots__ = ()

    def __new__(cls, *args):
        return BaseValidator(items_validators=args)


"""
Aliases for supported types
That can be used with Annotated, Union and T[T]
These are defined here mainly to help with auto complete

    from dynaconf.typed import types as ts
    class Settings(Dynaconf):
        field: ts.Str
        # actually the same as
        field: str

"""
Str = str
Int = int
Float = float
Bool = bool
NoneType = type(None)  # python 3.9 doesn't have types.NoneType
List = list
Tuple = tuple
Dict = dict
Numeric = Union[int, float]

SUPPORTED_TYPES = (
    Str,
    Int,
    Float,
    Bool,
    NoneType,
    List,
    Tuple,
    Dict,
    DictValue,
)
