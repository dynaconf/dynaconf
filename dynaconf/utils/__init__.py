import os
import warnings
from json import JSONDecoder


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


def object_merge(old, new, unique=False, tail=None):
    """
    Recursively merge two data structures, new is mutated in-place.

    :param old: The existing data.
    :param new: The new data to get old values merged in to.
    :param unique: When set to True existing list items are not set.
    :param tail: Indicates the last element of a tree.
    """
    if old == new or old is None or new is None:
        # Nothing to merge
        return

    if isinstance(old, list) and isinstance(new, list):
        for item in old[::-1]:
            if unique and item in new:
                continue
            new.insert(0, item)

    if isinstance(old, dict) and isinstance(new, dict):
        for key, value in old.items():
            if key == tail:
                continue
            if key not in new:
                new[key] = value
            else:
                object_merge(value, new[key], tail=tail)

        handle_metavalues(old, new)

    return new


def handle_metavalues(old, new):
    """Cleanup of MetaValues on new dict"""
    for key in list(new.keys()):
        if getattr(new[key], "_dynaconf_reset", False):  # pragma: no cover
            # a Reset on `new` triggers reasign of existing data
            # @reset is deprecated on v3.0.0
            new[key] = new[key].unwrap()

        if getattr(new[key], "_dynaconf_merge", False):
            # a Merge on `new` triggers merge with existing data
            new[key] = object_merge(
                old.get(key), new[key].unwrap(), unique=new[key].unique
            )

        if getattr(new[key], "_dynaconf_del", False):
            # a Del on `new` triggers deletion of existing data
            new.pop(key, None)
            old.pop(key, None)


class DynaconfDict(dict):
    """A dict representing en empty Dynaconf object
    useful to run loaders in to a dict for testing"""

    def __init__(self, *args, **kwargs):
        self._loaded_files = []
        super(DynaconfDict, self).__init__(*args, **kwargs)

    def set(self, key, value, *args, **kwargs):
        self[key] = value

    @staticmethod
    def get_environ(key, default=None):  # pragma: no cover
        return os.environ.get(key, default)

    def exists(self, key, **kwargs):
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


def compat_kwargs(kwargs):
    """To keep backwards compat change the kwargs to new names"""
    warn_deprecations(kwargs)
    for old, new in RENAMED_VARS.items():
        if old in kwargs:
            kwargs[new] = kwargs[old]
            # update cross references
            for c_old, c_new in RENAMED_VARS.items():
                if c_new == new:
                    kwargs[c_old] = kwargs[new]


class Missing(object):
    """
    Sentinel value object/singleton used to differentiate between ambiguous
    situations where `None` is a valid value.
    """

    def __bool__(self):
        """Respond to boolean duck-typing."""
        return False

    def __eq__(self, other):
        """Equality check for a singleton."""

        return isinstance(other, self.__class__)

    # Ensure compatibility with Python 2.x
    __nonzero__ = __bool__

    def __repr__(self):
        """
        Unambiguously identify this string-based representation of Missing,
        used as a singleton.
        """
        return "<dynaconf.missing>"


missing = Missing()


def deduplicate(list_object):
    """Rebuild `list_object` removing duplicated and keeping order"""
    new = []
    for item in list_object:
        if item not in new:
            new.append(item)
    return new


def warn_deprecations(data):
    for old, new in RENAMED_VARS.items():
        if old in data:
            warnings.warn(
                f"You are using {old} which is a deprecated settings "
                f"replace it with {new}",
                DeprecationWarning,
            )


def trimmed_split(s, seps=(";", ",")):
    """Given a string s, split is by one of one of the seps."""
    for sep in seps:
        if sep not in s:
            continue
        data = [item.strip() for item in s.strip().split(sep)]
        return data
    return [s]  # raw un-splitted


def ensure_a_list(data):
    """Ensure data is a list or wrap it in a list"""
    if not data:
        return []
    if isinstance(data, (list, tuple, set)):
        return list(data)
    if isinstance(data, str):
        data = trimmed_split(data)  # settings.toml,other.yaml
        return data
    return [data]


def build_env_list(obj, env):
    """Build env list for loaders to iterate.

    Arguments:
        obj {LazySettings} -- A Dynaconf settings instance
        env {str} -- The current env to be loaded

    Returns:
        [str] -- A list of string names of the envs to load.
    """
    # add the [default] env
    env_list = [obj.get("DEFAULT_ENV_FOR_DYNACONF")]

    # compatibility with older versions that still uses [dynaconf] as
    # [default] env
    global_env = obj.get("ENVVAR_PREFIX_FOR_DYNACONF") or "DYNACONF"
    if global_env not in env_list:
        env_list.append(global_env)

    # add the current env
    if obj.current_env and obj.current_env not in env_list:
        env_list.append(obj.current_env)

    # add a manually set env
    if env and env not in env_list:
        env_list.append(env)

    # add the [global] env
    env_list.append("GLOBAL")

    # loaders are responsible to change to lower/upper cases
    return [env.lower() for env in env_list]


def upperfy(key):
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


def multi_replace(text, patterns):
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


def extract_json_objects(text, decoder=JSONDecoder()):
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


def recursively_evaluate_lazy_format(value, settings):

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
