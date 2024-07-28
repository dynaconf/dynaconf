from __future__ import annotations  # WARNING: remove this when debugging

import types
from typing import Annotated
from typing import TypeVar
from typing import Union

from . import utils as ut
from .exceptions import DynaconfSchemaError
from .parser import parse_schema

T = TypeVar("T")


class NotRequiredMarker:
    _dynaconf_notrequired = True
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


class M(type):
    __dict_class_methods__ = ["copy", "fromkeys", "mro"]
    __dict_methods__ = [
        "clear",
        "get",
        "items",
        "keys",
        "pop",
        "popitem",
        "setdefault",
        "update",
        "values",
    ]

    def __new__(cls, name, bases, namespace):
        if namespace["__module__"] != __name__:
            # Rules applies only to subclasses
            annotations = namespace.get("__annotations__")
            dunders = [item for item in dir(cls) if item.startswith("_")]
            dunders.append("__annotations__")  # for python 3.9
            attributes = [k for k in namespace if k not in dunders]
            namespace["__reserved__"] = {}
            for attr in attributes:
                if attr not in annotations:
                    if isinstance(
                        namespace[attr],
                        (
                            types.FunctionType,
                            types.ClassMethodDescriptorType,
                            staticmethod,
                            classmethod,
                        ),
                    ):
                        raise DynaconfSchemaError(
                            f"Invalid method definition {attr!r}: "
                            "DataDict doesn't allow definition of methods. "
                            f"{name!r} is a dict-like object, use a separate "
                            "function that takes a 'dict'"
                        )

                    raise DynaconfSchemaError(
                        f"{attr!r} must include type annotation"
                    )

                if attr in cls.__dict_class_methods__ + cls.__dict_methods__:
                    namespace["__reserved__"][attr] = namespace.pop(attr)
        return super().__new__(cls, name, bases, namespace)


class DataDict(dict, metaclass=M):  # type: ignore
    """DataDict represents a Typed Dict in the settings.

    The typing.TypedDict could not be used because the constraints differs.

    The UserDict could not be used because it adds more reserved names for
    attr access.

    self.__data__ dict that holds the actual data.
    self.__reserved__ dict that holds any key part of the reserved words
    """

    __reserved__: dict
    __data__: dict

    _dynaconf_datadict = True  # a marker for validator_conditions.is_type_of

    # List of methods that when accessed are passed through to self.__data__
    __dict_methods__ = M.__dict_methods__

    __local_attributes__ = [
        "__data__",
        "__reserved__",
        "__defaults__",
        "__validators__",
        "__schema__",
    ]

    def __init__(self, _dict: dict | None = None, **kwargs):
        """Initialize the dict-like object with its defaults applied."""
        self.__schema__ = parse_schema(self.__class__)
        data = ut.multi_dict_merge(self.__schema__.defaults, _dict, kwargs)
        self.__data__ = data

    def __setattr__(self, name, value):
        if name in self.__local_attributes__:
            return super().__setattr__(name, value)
        self.__data__[name] = value

    def __getattribute__(self, attr):
        dict_attrs = object.__getattribute__(self, "__dict_methods__")
        if attr in dict_attrs:
            data = object.__getattribute__(self, "__data__")
            return getattr(data, attr)
        return super().__getattribute__(attr)

    def __getitem__(self, item):
        return self.__data__[item]

    def __setitem__(self, item, value):
        self.__data__[item] = value

    def __getattr__(self, attr):
        try:
            data = object.__getattribute__(self, "__data__")
            return data[attr]
        except KeyError:
            raise AttributeError(
                f"{self.__class__.__name__!r} has no attribute {attr!r}"
            )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__data__.__repr__()})"

    def __contains__(self, other):
        return other in self.__data__

    def copy(self):
        return self.__class__(self.__data__.copy())

    def __eq__(self, other):
        return self.__data__ == other

    def __iter__(self):
        return iter(self.__data__)

    def __bool__(self):
        return bool(self.__data__)

    @classmethod
    def fromkeys(cls, iterable, value):
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
    DataDict,
)
