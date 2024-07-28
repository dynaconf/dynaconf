from __future__ import annotations  # WARNING: remove this when debugging

import json
from functools import reduce
from typing import Annotated
from typing import get_args
from typing import get_origin
from typing import Union

from dynaconf.utils.functional import empty

from .compat import UnionType


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
    """From annotation name: T[T, args] extract type, args."""
    _type_args: tuple = tuple()
    # _type from `field: T` or `field: list[T]`
    _type = get_origin(annotation) or annotation
    if _type is Annotated:
        _type, *_type_args = get_args(annotation)
    else:
        _type_args = get_args(annotation)
    return _type, _type_args


def is_notrequired(annotation):
    return is_annotated(annotation) and any(
        getattr(item, "_dynaconf_notrequired", None)
        for item in get_args(annotation)
    )


def is_annotated(annotation):
    return get_origin(annotation) is Annotated


def is_dict_value(annotation):
    return getattr(annotation, "_dynaconf_dictvalue", None)


def is_enclosed_list(_type, _type_args):
    return _type_args and _type in (list, tuple)


def is_union(annotation) -> bool:
    """Tell if an annotation is strictly Union."""
    return get_origin(annotation) in [Union, UnionType]


def maybe_dict_value(annotation):
    return is_union(annotation) and any(
        is_dict_value(item) for item in get_args(annotation)
    )


def get_class_from_type_args(type_args):
    for arg in type_args:
        if is_dict_value(arg):
            return arg


def is_dict_value_in_a_dict(annotation):
    origin = get_origin(annotation)
    args = get_args(annotation)
    return origin is dict and len(args) == 2 and is_dict_value(args[1])


def is_optional(annotation) -> bool:
    """Tell if an annotation is strictly typing.Optional or Union[**, None]"""
    return is_union(annotation) and get_args(annotation)[1] == type(None)


def is_type(value) -> bool:
    _type = get_origin(value) or value
    return isinstance(_type, type) or is_union(value) or is_optional(value)


def dict_merge(d1: dict, d2: dict) -> dict:
    """Takes two dictionaries d1 and d2 and merges their data

    Example:

        >>> d1 = {'name': 'John', 'profile': {'group': 1, 'team': 42}}
        >>> d2 = {'profile': {'username': 'jj', 'group': 2}}
        >>> d3 = dict_merge(d1, d2)
        >>> d3 == {'name': 'John', 'profile': {'group': 2, 'team': 42, 'username': 'jj'}}
    """
    if not isinstance(d2, dict):
        return d1

    merged = d1.copy()

    for key, value in d2.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = dict_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def multi_dict_merge(*dicts) -> dict:
    """Reduces merge of a list of dicts."""
    return reduce(dict_merge, dicts)


def dump_debug_info(init_options, validators, schema):
    """Debug utility to be removed later"""
    dump = __builtins__["print"]  # cheat the linter

    # pdump = __import__("pprint").pp
    def jdump(v):
        return dump(json.dumps(v, indent=2, sort_keys=True, default=str))

    def tdump(text, char="*", offset=0, s=""):
        return dump(
            "{s}{o}{:{c}^80}".format(f" {text} ", c=char, o=" " * offset, s=s)
        )

    tdump("INIT DEFAULTS", s="\n")
    jdump(init_options)

    tdump("VALIDATORS", s="\n")
    for i, validator in enumerate(validators, 1):
        tdump(validator.names[0].upper(), "#")
        dump(i, validator)

        def print_all_validators(v, prefix):
            if v.items_validators:
                tdump(v.names[0].upper(), "-", len(prefix))
                for n, item_v in enumerate(v.items_validators, 1):
                    tdump(f"{prefix}.{n}", "_", len(prefix))
                    dump(" " * len(prefix), item_v)
                    print_all_validators(item_v, f"{prefix}.{n}")

        print_all_validators(validator, prefix=str(i))

    tdump("SCHEMA", s="\n")
    jdump(schema.as_dict())

    tdump("END", s="\n")


def aggregate_dict_schema_defaults(dict_schema, data):
    """Aggregated defaults from data on top of dict_schema defaults"""
    # merge default with default from type
    # NOTE: What to do in case of Lazy data?
    #       @json @format {....}
    dict_schema_defaults = dict_schema.__get_defaults__()
    if isinstance(data, dict) and dict_schema_defaults:
        data = dict_merge(dict_schema_defaults, data)
    elif data is empty and dict_schema_defaults:
        data = dict_schema_defaults
    return data
