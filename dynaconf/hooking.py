from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any
from typing import Callable

__all__ = [
    "hookable",
    "EMPTY_VALUE",
    "Hook",
    "EagerValue",
    "HookValue",
    "MethodValue",
    "Action",
]


class Empty:
    ...


EMPTY_VALUE = Empty()


def hookable(function=None, name=None, before=True, after=True):
    """Adds before and after hooks to any method.

    :param function: function to be decorated
    :param name: name of the method to be decorated (default to method name)
    :param before: if before hooks should be executed
    :param after: if after hooks should be executed
    :return: decorated function

    Usage: see tests/test_hooking.py for more examples.
    """

    if function and not callable(function):
        raise TypeError("hookable must be applied with named arguments only")

    def dispatch(fun, *args, **kwargs):
        """calls the decorated function and its hooks"""
        self, *args = args
        # _registered_hooks = getattr(self, "_registered_hooks", None)
        hooks_key, _registered_hooks = pop_hooks(self)
        if not _registered_hooks:
            return fun(self, *args, **kwargs)

        def _hook(self, action, value, *args, **kwargs):
            function_name = name or fun.__name__
            hooks = _registered_hooks.get(f"{action}_{function_name}", [])
            for hook in hooks:
                value, args, kwargs = hook.function(
                    self, value, *args, **kwargs
                )
                value = HookValue.new(value)
            return value, args, kwargs

        value = HookValue(EMPTY_VALUE)
        if before:
            value, args, kwargs = _hook(self, "before", value, *args, **kwargs)

        if not isinstance(value, EagerValue):
            value = HookValue.new(fun(self, *args, **kwargs))

        if after:
            value, args, kwargs = _hook(self, "after", value, *args, **kwargs)

        # Put back registered hooks on self
        put_hooks(self, _registered_hooks, hooks_key)

        return value.value

    if function:
        # decorator applied without parameters e.g: @hookable
        @wraps(function)
        def wrapper(*args, **kwargs):
            return dispatch(function, *args, **kwargs)

        # wrapper.function = function
        return wrapper

    def decorator(function):
        # decorator applied with parameters e.g: @hookable(before=False)
        @wraps(function)
        def wrapper(*args, **kwargs):
            return dispatch(function, *args, **kwargs)

        # wrapper.function = function
        return wrapper

    return decorator


def pop_hooks(obj):
    """Remove registered hooks from object"""
    return_name = "_registered_hooks"
    hooks = None
    for key in [return_name, return_name.upper()]:
        if hasattr(obj, key):
            return_name = key
            hooks = getattr(obj, key)
        elif isinstance(obj, dict) and key in obj:
            return_name = key
            hooks = obj[key]
        elif hasattr(obj, "_store") and key in obj._store:
            return_name = key
            hooks = obj._store[key]

    with suppress(Exception):
        delattr(obj, return_name)
    with suppress(Exception):
        del obj[return_name]
    with suppress(Exception):
        del obj._store[return_name]

    return return_name, hooks


def put_hooks(obj, hooks, key="_registered_hooks"):
    """Put back registered hooks on object"""
    if hasattr(obj, "_store"):
        obj._store[key] = hooks
    else:
        setattr(obj, key, hooks)


@dataclass
class Hook:
    """Hook to wrap a callable on _registered_hooks list.

    :param callable: The callable to be wrapped

    The callable must accept the following arguments:

    - self: The instance of the class, e.g `settings`
    - value: The value to be processed
      (accumulated from previous hooks, last hook will receive the final value)
    - *args: The args passed to the original method
    - **kwargs: The kwargs passed to the original method

    The callable must return a tuple with the following values:

    - value: The processed value to be passed to the next hook
    - *args: The args to be passed to the next hook
    - **kwargs: The kwargs to be passed to the next hook
    """

    function: Callable


@dataclass
class HookValue:
    """Base class for hook values.
    Hooks must return a HookValue instance.
    """

    value: Any

    @classmethod
    def new(cls, value: Any) -> HookValue:
        """Return a new HookValue instance with the given value."""
        if isinstance(value, HookValue):
            return value
        return cls(value)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        return self.value == other

    def __ne__(self, other) -> bool:
        return self.value != other

    def __bool__(self) -> bool:
        return bool(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __delitem__(self, key):
        del self.value[key]

    def __contains__(self, item):
        return item in self.value

    def __getattr__(self, item):
        return getattr(self.value, item)

    def __setattr__(self, key, value):
        if key == "value":
            super().__setattr__(key, value)
        else:
            setattr(self.value, key, value)

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __truediv__(self, other):
        return self.value / other

    def __floordiv__(self, other):
        return self.value // other

    def __mod__(self, other):
        return self.value % other

    def __divmod__(self, other):
        return divmod(self.value, other)

    def __pow__(self, power, modulo=None):
        return pow(self.value, power, modulo)

    def __delattr__(self, item):
        delattr(self.value, item)

    def __repr__(self) -> str:
        return repr(self.value)


@dataclass
class MethodValue(HookValue):
    """A value returned by a method
    The main decorated method have its value wrapped in this class
    """


@dataclass
class EagerValue(HookValue):
    """Use this wrapper to return earlier from a hook.
    Main function is bypassed and value is passed to after hooks."""


class Action(str, Enum):
    """All the hookable functions"""

    AFTER_AS_DICT = "after_as_dict"
    BEFORE_AS_DICT = "before_as_dict"
    AFTER_GET = "after_get"
    BEFORE_GET = "before_get"
    AFTER_SET = "after_set"
    BEFORE_SET = "before_set"
    AFTER_UPDATE = "after_update"
    BEFORE_UPDATE = "before_update"
    AFTER_LOADERS = "after_loaders"
    BEFORE_LOADERS = "before_loaders"
    AFTER_LOAD_FILE = "after_load_file"
    BEFORE_LOAD_FILE = "before_load_file"
    AFTER_POPULATE_OBJ = "after_populate_obj"
    BEFORE_POPULATE_OBJ = "before_populate_obj"
