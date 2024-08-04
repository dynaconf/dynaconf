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
            _annotations = namespace.get("__annotations__")
            dunders = [item for item in dir(cls) if item.startswith("_")]
            dunders.append("__annotations__")  # for python 3.9
            attributes = [k for k in namespace if k not in dunders]
            namespace["__reserved__"] = {}
            for attr in attributes:
                if attr not in _annotations:
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
    """DataDict represents a Typed Dict in the settings."""

    __slots__ = ()
    __reserved__: dict
    _dynaconf_datadict = True  # a marker for validator_conditions.is_type_of
    __local_attributes__ = ["__reserved__", "__schema__"]

    def __init__(self, _dict: dict | None = None, **kwargs):
        """Initialize the dict-like object.

        - Parse schema (defaults, validators, spec)
        - Merge defaults from schema + dict parameters
        - Apply transformations from schema if defined
        """
        self.__schema__ = parse_schema(self.__class__)
        data = ut.multi_dict_merge(self.__schema__.defaults, _dict, kwargs)
        data = self.__schema__.apply_transformer_all(data)
        super().__init__(data)

    def __setitem__(self, key, value):
        value = self.__schema__.apply_transformer(key, value)
        super().__setitem__(key, value)

    def update(self, _dict, **kwargs):
        data = ut.multi_dict_merge(_dict, kwargs)
        data = self.__schema__.apply_transformer_all(data)
        super().update(data)

    def __setattr__(self, name, value):
        if name in self.__local_attributes__:
            return super().__setattr__(name, value)
        self[name] = value

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr) from None

    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self)})"

    def copy(self):
        return self.__class__(super().copy())


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
