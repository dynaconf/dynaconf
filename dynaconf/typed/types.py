from __future__ import annotations  # WARNING: remove this when debugging

from collections.abc import Sequence
from typing import Annotated
from typing import Any
from typing import Callable

from dynaconf.utils.functional import Empty
from dynaconf.utils.functional import empty
from dynaconf.validator import Validator as BaseValidator

from .compat import get_annotations

Annotated = Annotated


class DictValue:
    """A dictvalue Subtype is actually a Dict, so instantiating it just returns
    the dict."""

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
        # To be implemented, a interface like this to generate a When Validator
        # when: When | None = empty,
    ):
        kwargs = locals()
        kwargs.pop("cls")
        return BaseValidator(
            **{k: v for k, v in kwargs.items() if v is not empty}
        )
