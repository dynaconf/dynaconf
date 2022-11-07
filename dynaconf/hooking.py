from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any
from typing import Callable

from dynaconf.base import Settings


__all__ = [
    "hookable",
    "EMPTY_VALUE",
    "Hook",
    "EagerValue",
    "HookValue",
    "MethodValue",
    "Action",
    "HookableSettings",
]


class Empty:
    ...


EMPTY_VALUE = Empty()


def hookable(function=None, name=None):
    """Adds before and after hooks to any method.

    :param function: function to be decorated
    :param name: name of the method to be decorated (default to method name)
    :return: decorated function

    Usage: see tests/test_hooking.py for more examples.
    """

    if function and not callable(function):
        raise TypeError("hookable must be applied with named arguments only")

    def dispatch(fun, self, *args, **kwargs):
        """calls the decorated function and its hooks"""

        # If function is being called from inside a hook, return the original
        # if object has no hooks, return the original
        inside_a_hook = isinstance(self, SettingsWrapper)
        if inside_a_hook or not (_registered_hooks := get_hooks(self)):
            return fun(self, *args, **kwargs)

        function_name = name or fun.__name__

        # function being called not in the list of hooks, return the original
        if not set(_registered_hooks).intersection(
            (f"before_{function_name}", f"after_{function_name}")
        ):
            return fun(self, *args, **kwargs)

        # Wrap the instance in a wrapper that will be passed to the hooks
        # so they can access the instance attributes and methods without
        # triggering the hooks again
        self = SettingsWrapper(self, function_name)

        def _hook(action: str, value: HookValue) -> HookValue:
            """executes the hooks for the given action"""
            hooks = _registered_hooks.get(f"{action}_{function_name}", [])
            for hook in hooks:
                value = hook.function(self, value, *args, **kwargs)
                value = HookValue.new(value)
            return value

        # Value starts as en empty value on the first before hook
        value = _hook("before", HookValue(EMPTY_VALUE))

        # If the value is EagerValue, it means main function should not be
        # executed and the value should go straight to the after hooks if any
        if not isinstance(value, EagerValue):
            value = MethodValue(fun(self, *args, **kwargs))

        value = _hook("after", value)

        # unwrap the value from the HookValue so it can be returned
        # normally to the caller
        return value.value

    if function:
        # decorator applied without parameters e.g: @hookable
        @wraps(function)
        def wrapper(*args, **kwargs):
            return dispatch(function, *args, **kwargs)

        wrapper.original_function = function
        return wrapper

    def decorator(function):
        # decorator applied with parameters e.g: @hookable(before=False)
        @wraps(function)
        def wrapper(*args, **kwargs):
            return dispatch(function, *args, **kwargs)

        wrapper.original_function = function
        return wrapper

    return decorator


def get_hooks(obj):
    """get registered hooks from object"""
    attr = "_registered_hooks"
    for key in [attr, attr.upper()]:
        if hasattr(obj, key):
            return getattr(obj, key)
        elif isinstance(obj, dict) and key in obj:
            return obj[key]
        elif hasattr(obj, "_store") and key in obj._store:
            return obj._store[key]


class SettingsWrapper:
    """Allow hooks to access the original object without recursion"""

    def __init__(self, settings, function_name):
        self.settings = settings
        original_function = getattr(settings, function_name).original_function
        setattr(
            self,
            function_name,
            lambda *args, **kwargs: original_function(self, *args, **kwargs),
        )

    def __getattr__(self, item):
        if item.lower() == "_registered_hooks":
            return None
        return getattr(self.settings, item)

    def __getitem__(self, item):
        if item == "_registered_hooks":
            return None
        return self.settings[item]


@dataclass
class Hook:
    """Hook to wrap a callable on _registered_hooks list.

    :param callable: The callable to be wrapped

    The callable must accept the following arguments:

    - self: The instance of the class, e.g `settings`
    - value: The value to be processed wrapper in a HookValue
      (accumulated from previous hooks, last hook will receive the final value)
    - *args: The args passed to the original method
    - **kwargs: The kwargs passed to the original method

    The callable must return a tuple with the following values:

    - value: The processed value to be passed to the next hook
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


class HookableSettings(Settings):
    """Wrapper for dynaconf.base.Settings that adds hooks to methods."""

    @hookable
    def as_dict(self, *args, **kwargs):
        return Settings.as_dict(self, *args, **kwargs)

    to_dict = as_dict

    @hookable
    def get(self, *args, **kwargs):
        return Settings.get(self, *args, **kwargs)

    @hookable
    def set(self, *args, **kwargs):
        return Settings.set(self, *args, **kwargs)

    @hookable
    def update(self, *args, **kwargs):
        return Settings.update(self, *args, **kwargs)

    @hookable(name="loaders")
    def execute_loaders(self, *args, **kwargs):
        return Settings.execute_loaders(self, *args, **kwargs)

    @hookable
    def load_file(self, *args, **kwargs):
        return Settings.load_file(self, *args, **kwargs)

    @hookable
    def populate_obj(self, *args, **kwargs):
        return Settings.populate_obj(self, *args, **kwargs)
