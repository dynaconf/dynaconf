# coding: utf-8
import os
import logging
import warnings

BANNER = """
██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝
"""

if os.name == 'nt':  # pragma: no cover
    # windows can't handle the above charmap
    BANNER = "DYNACONF"


def object_merge(old, new, unique=False):
    """
    Recursively merge two data structures.

    :param unique: When set to True existing list items are not set.
    """
    if isinstance(old, list) and isinstance(new, list):
        if old == new:
            return
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


def raw_logger():
    """Get or create inner logger"""
    level = os.environ.get('DEBUG_LEVEL_FOR_DYNACONF', 'ERROR')
    try:  # pragma: no cover
        from logzero import setup_logger
        return setup_logger(
            "dynaconf",
            level=getattr(logging, level)
        )
    except ImportError:  # pragma: no cover
        logger = logging.getLogger("dynaconf")
        logger.setLevel(getattr(logging, level))
        return logger


RENAMED_VARS = {
    # old: new
    'DYNACONF_NAMESPACE': 'ENV_FOR_DYNACONF',
    'NAMESPACE_FOR_DYNACONF': 'ENV_FOR_DYNACONF',
    'DYNACONF_SETTINGS_MODULE': 'SETTINGS_MODULE_FOR_DYNACONF',
    'DYNACONF_SETTINGS': 'SETTINGS_MODULE_FOR_DYNACONF',
    'SETTINGS_MODULE': 'SETTINGS_MODULE_FOR_DYNACONF',
    'PROJECT_ROOT': 'ROOT_PATH_FOR_DYNACONF',
    'PROJECT_ROOT_FOR_DYNACONF': 'ROOT_PATH_FOR_DYNACONF',
    'DYNACONF_SILENT_ERRORS': 'SILENT_ERRORS_FOR_DYNACONF',
    'DYNACONF_ALWAYS_FRESH_VARS': 'FRESH_VARS_FOR_DYNACONF',
    'BASE_NAMESPACE_FOR_DYNACONF': 'DEFAULT_ENV_FOR_DYNACONF'
}


def compat_kwargs(kwargs):
    """To keep backwards compat change the kwargs to new names"""
    warn_deprecations(kwargs)
    for old, new in RENAMED_VARS.items():
        if old in kwargs:
            kwargs[new] = kwargs[old]


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
        return '<dynaconf.missing>'


missing = Missing()


def deduplicate(list_object):
    """Rebuild `list_object` removing duplicated and keeping order"""
    new = []
    for item in list_object:
        if item not in new:
            new.append(item)
    return new


def warn_deprecations(data):
    if data.get('MERGE_ENABLED_FOR_DYNACONF'):
        warnings.warn(
            "MERGE_ENABLED_FOR_DYNACONF is deprecated "
            "instead it is prefered to use the local merge feature "
            "see: https://dynaconf.readthedocs.io/en/latest/guides/usage.html"
            "#merging-existing-values",
            DeprecationWarning
        )
    for old, new in RENAMED_VARS.items():
        if old in data:
            warnings.warn(
                "You are using %s which is a deprecated settings "
                "replace it with %s" % (old, new),
                DeprecationWarning
            )
