import functools
import os
import warnings


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


def object_merge(old, new, unique=False):
    """
    Recursively merge two data structures.

    :param unique: When set to True existing list items are not set.
    """
    if old == new:
        # Nothing to merge
        return

    if isinstance(old, list) and isinstance(new, list):
        for item in old[::-1]:
            if unique and item in new:
                continue
            new.insert(0, item)
    if isinstance(old, dict) and isinstance(new, dict):
        for key, value in old.items():
            if key not in new:
                new[key] = value
            else:
                object_merge(value, new[key])

        # Cleanup of MetaValues on New dict
        for key, value in new.items():
            if getattr(new[key], "dynaconf_reset", False):
                # new Reset triggers cleanup of existing data
                new[key] = new[key].value
            elif getattr(new[key], "dynaconf_del", False):
                # new Del triggers deletion of existing data
                new.pop(key, None)


class DynaconfDict(dict):
    """A dict representing en empty Dynaconf object
    useful to run loaders in to a dict for testing"""

    def __init__(self, *args, **kwargs):
        self._loaded_files = []
        super(DynaconfDict, self).__init__(*args, **kwargs)

    @property
    def logger(self):
        return raw_logger()

    def set(self, key, value, *args, **kwargs):
        self[key] = value

    @staticmethod
    def get_environ(key, default=None):  # pragma: no cover
        return os.environ.get(key, default)

    def exists(self, key, **kwargs):
        return self.get(key, missing) is not missing


@functools.lru_cache()
def _logger(level):
    import logging

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s,%(msecs)d %(levelname)-8s "
            "[%(filename)s:%(lineno)d - %(funcName)s] %(message)s"
        ),
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger("dynaconf")
    logger.addHandler(handler)
    logger.setLevel(level=getattr(logging, level, "DEBUG"))
    return logger


def raw_logger(level=None):
    """Get or create inner logger"""
    level = level or os.environ.get("DEBUG_LEVEL_FOR_DYNACONF", "ERROR")
    return _logger(level)


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
                "You are using %s which is a deprecated settings "
                "replace it with %s" % (old, new),
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
    if "__" in key:
        parts = key.split("__")
        return "__".join([parts[0].upper()] + parts[1:])
    return key.upper()
