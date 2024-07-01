import sys


def _get_annotations_for_python_39(schema_cls) -> dict:
    if isinstance(schema_cls, type):
        return schema_cls.__dict__.get("__annotations__", {})
    else:
        return getattr(schema_cls, "__annotations__", {})


if sys.version_info < (3, 10):
    from typing import Union

    UnionType = Union
    get_annotations = _get_annotations_for_python_39
else:
    from inspect import get_annotations
    from types import UnionType


__all__ = [
    "get_annotations",
    "UnionType",
]
