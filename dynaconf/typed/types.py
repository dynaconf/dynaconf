from __future__ import annotations  # WARNING: remove this when debugging

from typing import Annotated
from typing import get_args
from typing import get_origin
from typing import TypeVar
from typing import Union

from dynaconf.utils.functional import empty

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


class DictValue(dict):
    """DictValue represents a Typed Dict in the settings.

    The typing.TypedDict could not be used because the constraints differs.

    The UseDict could not be used because it adds more reserved names for
    attr access.
    """

    _dynaconf_dictvalue = True  # a marker for validator_conditions.is_type_of
    __dict_attributes__ = [
        "clear",
        # 'copy',  # Reimplemented
        # 'fromkeys',  # Reimplemented
        "get",
        "items",
        "keys",
        "pop",
        "popitem",
        "setdefault",
        "update",
        "values",
    ]
    __local_attributes__ = ["__defaults__", "__data__"]

    def __init__(self, _dict: dict | None = None, **kwargs):
        """Initialize a DictValue.
        Validates only the existence of required keys but does not validate
        types as types are going to be validated lazily by Dynaconf validation.
        """
        _dict = _dict or {}
        self.__defaults__ = self.__get_defaults__()
        data = self.__defaults__ | _dict | kwargs
        self.__validate_required_keys__(data)
        self.__data__ = data

    def __setattr__(self, name, value):
        if name in self.__local_attributes__:
            return super().__setattr__(name, value)
        self.__data__[name] = value

    def __getattribute__(self, attr):
        dict_attrs = object.__getattribute__(self, "__dict_attributes__")
        if attr in dict_attrs:
            data = object.__getattribute__(self, "__data__")
            return getattr(data, attr)
        if attr == "copy":
            return self.__copy__
        if attr == "fromkeys":
            return self.__fromkeys__
        return super().__getattribute__(attr)

    def __getitem__(self, item):
        return self.__data__[item]

    def __setitem__(self, item, value):
        self.__data__[item] = value

    def __getattr__(self, attr):
        try:
            return self.__data__[attr]
        except KeyError:
            raise AttributeError(
                f"{self.__class__.__name__!r} has no attribute {attr!r}"
            )

    @classmethod
    def __validate_required_keys__(cls, data):
        for key, annotation in get_annotations(cls).items():
            if get_origin(annotation) is Annotated and any(
                isinstance(item, NotRequiredMarker)
                for item in get_args(annotation)
            ):
                # skip NotRequired[T]
                continue

            if key not in data:
                raise TypeError(f"{key} is required.")

    @classmethod
    def __get_defaults__(cls):
        defaults = {}
        schema_annotations = get_annotations(cls)
        for name, annotation in schema_annotations.items():
            value = getattr(cls, name, empty)
            if value is not empty:
                defaults[name] = value
        return defaults

    def __repr__(self):
        return f"DictValue({self.__data__.__repr__()})"

    def __contains__(self, other):
        return other in self.__data__

    def __copy__(self):
        return self.__class__(self.__data__.copy())

    def __eq__(self, other):
        return self.__data__ == other

    def __iter__(self):
        return iter(self.__data__)

    @classmethod
    def __fromkeys__(cls, iterable, value):
        data = dict.fromkeys(iterable, value)
        return cls(data)


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
