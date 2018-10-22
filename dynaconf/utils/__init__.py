# coding: utf-8
import os
import logging

BANNER = """
██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝
"""


def object_merge(old, new):
    """
    Recursively merge two data structures
    """
    if isinstance(old, list) and isinstance(new, list):
        for item in old[::-1]:
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
        _no_project_root = kwargs.pop('_no_project_root', None)
        if not _no_project_root:
            self.PROJECT_ROOT_FOR_DYNACONF = '.'
        super(DynaconfDict, self).__init__(*args, **kwargs)

    @property
    def logger(self):
        return raw_logger()

    def set(self, key, value, *args, **kwargs):
        self[key] = value

    @staticmethod
    def get_environ(key, default=None):  # pragma: no cover
        return os.environ.get(key, default)


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


def compat_kwargs(kwargs):
    """To keep backwards compat change the kwargs to new names"""
    rules = {
        'DYNACONF_NAMESPACE': 'ENV_FOR_DYNACONF',
        'NAMESPACE_FOR_DYNACONF': 'ENV_FOR_DYNACONF',
        'DYNACONF_SETTINGS_MODULE': 'SETTINGS_MODULE_FOR_DYNACONF',
        'SETTINGS_MODULE': 'SETTINGS_MODULE_FOR_DYNACONF',
        'PROJECT_ROOT': 'PROJECT_ROOT_FOR_DYNACONF',
        'DYNACONF_SILENT_ERRORS': 'SILENT_ERRORS_FOR_DYNACONF',
        'DYNACONF_ALWAYS_FRESH_VARS': 'FRESH_VARS_FOR_DYNACONF'
    }
    for old, new in rules.items():
        if old in kwargs:
            raw_logger().warning(
                "You are using %s which is a deprecated settings "
                "replace it with %s",
                old, new
            )
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
