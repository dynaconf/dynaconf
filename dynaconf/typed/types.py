from __future__ import annotations  # WARNING: remove this when debugging

import types
from typing import Annotated
from typing import TypeVar
from typing import Union

from dynaconf.utils.functional import empty

from . import utils as ut
from .compat import get_annotations
from .exceptions import DynaconfSchemaError

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
                            "DictValue doesn't allow definition of methods. "
                            f"{name!r} is a dict-like object, use a separate "
                            "function that takes a 'dict'"
                        )

                    raise DynaconfSchemaError(
                        f"{attr!r} must include type annotation"
                    )

                if attr in cls.__dict_class_methods__ + cls.__dict_methods__:
                    namespace["__reserved__"][attr] = namespace.pop(attr)
        return super().__new__(cls, name, bases, namespace)


class DictValue(dict, metaclass=M):  # type: ignore
    """DictValue represents a Typed Dict in the settings.

    The typing.TypedDict could not be used because the constraints differs.

    The UserDict could not be used because it adds more reserved names for
    attr access.

    self.__data__ dict that holds the actual data.
    self.__reserved__ dict that holds any key part of the reserved words
    """

    _dynaconf_dictvalue = True  # a marker for validator_conditions.is_type_of

    # List of methods that when accessed are passed through to self.__data__
    __dict_methods__ = M.__dict_methods__

    __local_attributes__ = ["__data__", "__reserved__"]

    def __init__(self, _dict: dict | None = None, **kwargs):
        """Initialize the dict-like object with its defaults applied."""
        data = ut.multi_dict_merge(self.__get_defaults__(), _dict, kwargs)
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
            return self.__data__[attr]
        except KeyError:
            raise AttributeError(
                f"{self.__class__.__name__!r} has no attribute {attr!r}"
            )

    @classmethod
    def __get_defaults__(cls):
        defaults = {}
        schema_annotations = get_annotations(cls)
        for name, annotation in schema_annotations.items():
            # deal with attributes named against reserved methods e.g: copy
            value = cls.__reserved__.get(name, getattr(cls, name, empty))
            value_is_method = isinstance(value, types.MethodDescriptorType)

            if value is not empty and not value_is_method:
                # set default earlier, so if it is a Lazy str it resolves later
                defaults[name] = value

            # Annotation[T, args], list[T], NotRequired[T], dict[T,T]
            is_notrequired = ut.is_notrequired(annotation)
            target_type, type_args = ut.get_type_and_args(annotation)

            if ut.is_dict_value(target_type):
                if isinstance(value, target_type):
                    defaults[name] = value
                elif isinstance(value, dict):
                    defaults[name] = target_type(value)
                elif not is_notrequired:
                    defaults[name] = target_type()
            elif (
                ut.is_enclosed_list(target_type, type_args)  # list[T]
                and ut.is_dict_value(type_args[0])  # list[DataDict]
                and isinstance(defaults.get(name), list)  # list[T] = [...]
            ):
                for i, item in enumerate(defaults[name]):
                    if isinstance(item, dict):
                        defaults[name][i] = type_args[0](item)
            elif (
                ut.is_optional(annotation)  # Optional[T]
                and ut.is_dict_value(type_args[0])  # Optional[DataDict]
                and isinstance(
                    defaults.get(name), dict
                )  # Optional[...] = {...}
            ):
                defaults[name] = type_args[0](defaults[name])
            elif (
                ut.maybe_dict_value(annotation)  # Union[DataDict, T]
                and isinstance(defaults.get(name), dict)  # Union[...] = {}
            ):
                defaults[name] = type_args[0](defaults[name])

        return defaults

    def __repr__(self):
        return (
            f"{self.__class__.__name__}<DataDict>({self.__data__.__repr__()})"
        )

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
    DictValue,
)
