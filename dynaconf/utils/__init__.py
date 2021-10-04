from __future__ import annotations

import os
import warnings
from collections import defaultdict
from json import JSONDecoder
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union


if TYPE_CHECKING:  # pragma: no cover
    from dynaconf.utils.boxing import DynaBox
    from dynaconf.base import LazySettings, Settings


BANNER = """
██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝
"""

if os.name == "nt":  # pragma: no cover
    # windows can't handle the above charmap
    BANNER = "DYNACONF"


def object_merge(
    old: Any, new: Any, unique: bool = False, full_path: List[str] = None
) -> Any:
    """
    Recursively merge two data structures, new is mutated in-place.

    :param old: The existing data.
    :param new: The new data to get old values merged in to.
    :param unique: When set to True existing list items are not set.
    :param full_path: Indicates the elements of a tree.
    """
    if full_path is None:
        full_path = []
    if old == new or old is None or new is None:
        # Nothing to merge
        return new

    if isinstance(old, list) and isinstance(new, list):
        for item in old[::-1]:
            if unique and item in new:
                continue
            new.insert(0, item)

    if isinstance(old, dict) and isinstance(new, dict):
        existing_value = recursive_get(old, full_path)  # doesnt handle None
        # Need to make every `None` on `_store` to be an wrapped `LazyNone`

        for key, value in old.items():

            if (
                existing_value is not None
                and key.lower() == full_path[-1].lower()
                and existing_value is value
            ):
                # Here Be The Dragons
                # This comparison needs to be smarter
                continue

            if key not in new:
                new[key] = value
            else:
                object_merge(
                    value,
                    new[key],
                    full_path=full_path[1:] if full_path else None,
                )

        handle_metavalues(old, new)

    return new


def recursive_get(
    obj: Union[DynaBox, Dict[str, int], Dict[str, Union[str, int]]],
    names: Optional[List[str]],
) -> Any:
    """Given a dot accessible object and a list of names `foo.bar.zaz`
    gets recursivelly all names one by one obj.foo.bar.zaz.
    """
    if not names:
        return
    head, tail = names[0], names[1:]
    result = getattr(obj, head, None)
    if not tail:
        return result
    return recursive_get(result, tail)


def handle_metavalues(
    old: Union[DynaBox, Dict[str, int], Dict[str, Union[str, int]]], new: Any
) -> None:
    """Cleanup of MetaValues on new dict"""

    for key in list(new.keys()):

        # MetaValue instances
        if getattr(new[key], "_dynaconf_reset", False):  # pragma: no cover
            # a Reset on `new` triggers reasign of existing data
            # @reset is deprecated on v3.0.0
            new[key] = new[key].unwrap()
        elif getattr(new[key], "_dynaconf_del", False):
            # a Del on `new` triggers deletion of existing data
            new.pop(key, None)
            old.pop(key, None)
        elif getattr(new[key], "_dynaconf_merge", False):
            # a Merge on `new` triggers merge with existing data
            new[key] = object_merge(
                old.get(key), new[key].unwrap(), unique=new[key].unique
            )

        # Data structures containing merge tokens
        if isinstance(new.get(key), (list, tuple)):
            has_merge = "dynaconf_merge" in new[key]
            has_merge_unique = "dynaconf_merge_unique" in new[key]
            if has_merge or has_merge_unique:
                value = list(new[key])
                unique = False

                try:
                    value.remove("dynaconf_merge")
                except ValueError:
                    value.remove("dynaconf_merge_unique")
                    unique = True

                for item in old.get(key)[::-1]:
                    if unique and item in value:
                        continue
                    value.insert(0, item)

                new[key] = value

        elif isinstance(new.get(key), dict):
            local_merge = new[key].pop(
                "dynaconf_merge", new[key].pop("dynaconf_merge_unique", None)
            )
            if local_merge not in (True, False, None) and not new[key]:
                # In case `dynaconf_merge:` holds value not boolean - ref #241
                new[key] = local_merge

            if local_merge:
                new[key] = object_merge(old.get(key), new[key])


class DynaconfDict(dict):
    """A dict representing en empty Dynaconf object
    useful to run loaders in to a dict for testing"""

    def __init__(self, *args, **kwargs):
        self._fresh = False
        self._loaded_envs = []
        self._loaded_hooks = defaultdict(dict)
        self._loaded_py_modules = []
        self._loaded_files = []
        self._deleted = set()
        self._store = {}
        self._env_cache = {}
        self._loaded_by_loaders = {}
        self._loaders = []
        self._defaults = {}
        self.environ = os.environ
        self.SETTINGS_MODULE = None
        self.filter_strategy = kwargs.get("filter_strategy", None)
        self._not_installed_warnings = []
        self._validate_only = kwargs.pop("validate_only", None)
        self._validate_exclude = kwargs.pop("validate_exclude", None)
        super(DynaconfDict, self).__init__(*args, **kwargs)

    def set(self, key: str, value: str, *args, **kwargs) -> None:
        self[key] = value

    @staticmethod
    def get_environ(key, default=None):  # pragma: no cover
        return os.environ.get(key, default)

    def exists(self, key: str, **kwargs) -> bool:
        return self.get(key, missing) is not missing


RENAMED_VARS = {
    # old: new
    "DYNACONF_NAMESPACE": "ENV_FOR_DYNACONF",
    "NAMESPACE_FOR_DYNACONF": "ENV_FOR_DYNACONF",
    "DYNACONF_SETTINGS_MODULE": "SETTINGS_FILE_FOR_DYNACONF",
    "DYNACONF_SETTINGS": "SETTINGS_FILE_FOR_DYNACONF",
    "SETTINGS_MODULE": "SETTINGS_FILE_FOR_DYNACONF",
    "SETTINGS_MODULE_FOR_DYNACONF": "SETTINGS_FILE_FOR_DYNACONF",
    "PROJECT_ROOT": "ROOT_PATH_FOR_DYNACONF",
    "PROJECT_ROOT_FOR_DYNACONF": "ROOT_PATH_FOR_DYNACONF",
    "DYNACONF_SILENT_ERRORS": "SILENT_ERRORS_FOR_DYNACONF",
    "DYNACONF_ALWAYS_FRESH_VARS": "FRESH_VARS_FOR_DYNACONF",
    "BASE_NAMESPACE_FOR_DYNACONF": "DEFAULT_ENV_FOR_DYNACONF",
    "GLOBAL_ENV_FOR_DYNACONF": "ENVVAR_PREFIX_FOR_DYNACONF",
}


def compat_kwargs(kwargs: Dict[str, Any]) -> None:
    """To keep backwards compat change the kwargs to new names"""
    warn_deprecations(kwargs)
    for old, new in RENAMED_VARS.items():
        if old in kwargs:
            kwargs[new] = kwargs[old]
            # update cross references
            for c_old, c_new in RENAMED_VARS.items():
                if c_new == new:
                    kwargs[c_old] = kwargs[new]


class Missing:
    """
    Sentinel value object/singleton used to differentiate between ambiguous
    situations where `None` is a valid value.
    """

    def __bool__(self) -> bool:
        """Respond to boolean duck-typing."""
        return False

    def __eq__(self, other: Union[DynaBox, Missing]) -> bool:
        """Equality check for a singleton."""

        return isinstance(other, self.__class__)

    # Ensure compatibility with Python 2.x
    __nonzero__ = __bool__

    def __repr__(self) -> str:
        """
        Unambiguously identify this string-based representation of Missing,
        used as a singleton.
        """
        return "<dynaconf.missing>"


missing = Missing()


def deduplicate(list_object: List[str]) -> List[str]:
    """Rebuild `list_object` removing duplicated and keeping order"""
    new = []
    for item in list_object:
        if item not in new:
            new.append(item)
    return new


def warn_deprecations(data: Any) -> None:
    for old, new in RENAMED_VARS.items():
        if old in data:
            warnings.warn(
                f"You are using {old} which is a deprecated settings "
                f"replace it with {new}",
                DeprecationWarning,
            )


def trimmed_split(
    s: str, seps: Union[str, Tuple[str, str]] = (";", ",")
) -> List[str]:
    """Given a string s, split is by one of one of the seps."""
    for sep in seps:
        if sep not in s:
            continue
        data = [item.strip() for item in s.strip().split(sep)]
        return data
    return [s]  # raw un-splitted


def ensure_a_list(data: Any) -> Union[List[int], List[str]]:
    """Ensure data is a list or wrap it in a list"""
    if not data:
        return []
    if isinstance(data, (list, tuple, set)):
        return list(data)
    if isinstance(data, str):
        data = trimmed_split(data)  # settings.toml,other.yaml
        return data
    return [data]


def build_env_list(
    obj: Union[Settings, LazySettings], env: Optional[str]
) -> List[str]:
    """Build env list for loaders to iterate.

    Arguments:
        obj {LazySettings} -- A Dynaconf settings instance
        env {str} -- The current env to be loaded

    Returns:
        [str] -- A list of string names of the envs to load.
    """
    # add the [default] env
    env_list = [(obj.get("DEFAULT_ENV_FOR_DYNACONF") or "default").lower()]

    # compatibility with older versions that still uses [dynaconf] as
    # [default] env
    global_env = (obj.get("ENVVAR_PREFIX_FOR_DYNACONF") or "dynaconf").lower()
    if global_env not in env_list:
        env_list.append(global_env)

    # add the current env
    current_env = obj.current_env
    if current_env and current_env.lower() not in env_list:
        env_list.append(current_env.lower())

    # add a manually set env
    if env and env.lower() not in env_list:
        env_list.append(env.lower())

    # add the [global] env
    env_list.append("global")

    return env_list


def upperfy(key: str) -> str:
    """Receive a string key and returns its upper version.

    Example:

      input: foo
      output: FOO

      input: foo_bar
      output: FOO_BAR

      input: foo__bar__ZAZ
      output: FOO__bar__ZAZ

    Arguments:
        key {str} -- A string key that may contain dunders `__`

    Returns:
        The key as upper case but keeping the nested elements.
    """
    key = str(key)
    if "__" in key:
        parts = key.split("__")
        return "__".join([parts[0].upper()] + parts[1:])
    return key.upper()


def multi_replace(text: str, patterns: Dict[str, str]) -> str:
    """Replaces multiple pairs in a string

    Arguments:
        text {str} -- A "string text"
        patterns {dict} -- A dict of {"old text": "new text"}

    Returns:
        text -- str
    """
    for old, new in patterns.items():
        text = text.replace(old, new)
    return text


def extract_json_objects(
    text: str, decoder: JSONDecoder = JSONDecoder()
) -> Iterator[Dict[str, Union[int, Dict[Any, Any]]]]:
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    pos = 0
    while True:
        match = text.find("{", pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1


def recursively_evaluate_lazy_format(
    value: Any, settings: Union[Settings, LazySettings]
) -> Any:
    """Given a value as a data structure, traverse all its members
    to find Lazy values and evaluate it.

    For example: Evaluate values inside lists and dicts
    """

    if getattr(value, "_dynaconf_lazy_format", None):
        value = value(settings)

    if isinstance(value, list):
        # Keep the original type, can be a BoxList
        value = value.__class__(
            [
                recursively_evaluate_lazy_format(item, settings)
                for item in value
            ]
        )

    return value


def isnamedtupleinstance(value):
    """Check if value is a namedtuple instance

    stackoverflow.com/questions/2166818/
    how-to-check-if-an-object-is-an-instance-of-a-namedtuple
    """

    t = type(value)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(type(n) == str for n in f)
