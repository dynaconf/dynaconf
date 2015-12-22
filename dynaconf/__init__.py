"""
Dynamic Settings Loader.

Values will be read from the module specified by the DYNACONF_SETTINGS_MODULE
environment variable;
"""
import os
import types
import errno
import logging
import importlib
from contextlib import contextmanager
from dynaconf import default_settings
from dynaconf.utils.parse_conf import converters
from dynaconf.conf.exceptions import ImproperlyConfigured
from dynaconf.conf.functional import LazyObject, empty
from dynaconf.loaders import default_loader, module_loader


class LazySettings(LazyObject):
    """
    A lazy proxy for either global settings or a custom settings obj
    The user can manually configure settings prior to using them. Otherwise,
    uses the settings module pointed to by DYNACONF_SETTINGS_MODULE.
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(default_settings, k.upper(), v)
        super(LazySettings, self).__init__()

    def _setup(self, name=None):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has
        not previously configured the settings manually.
        """
        ENVIRONMENT_VARIABLE = default_settings.ENVVAR_FOR_DYNACONF
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            desc = ("setting %s" % name) if name else "settings"
            raise ImproperlyConfigured(
                "Requested %s, but settings are not configured. "
                "You must either define the environment variable %s "
                "or call settings.configure() before accessing settings."
                % (desc, ENVIRONMENT_VARIABLE))
        self._wrapped = Settings(settings_module)

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup(name)
        always_fresh = getattr(self._wrapped, 'DYNACONF_ALWAYS_FRESH_VARS')
        if self._wrapped._fresh or name in always_fresh:
            return self._wrapped.get_fresh(name)
        return getattr(self._wrapped, name)

    def configure(self, root=None,
                  default_settings=default_settings, **options):
        """
        Called to manually configure the settings. The 'default_settings'
        parameter sets where to retrieve any unspecified values from (its
        argument must support attribute access (__getattr__)).
        """
        if root:
            if root.startswith('/'):
                default_settings.PROJECT_ROOT = root
            else:
                default_settings.PROJECT_ROOT = os.path.realpath(root)

        if self._wrapped is not empty:
            raise RuntimeError('Settings already configured.')

        holder = UserSettingsHolder(default_settings)
        for name, value in options.items():
            setattr(holder, name, value)
        self._wrapped = holder

    @property
    def configured(self):
        """
        Returns True if the settings have already been configured.
        """
        return self._wrapped is not empty

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class BaseSettings(object):
    """
    Common logic for settings whether set by a module or by the user.
    """
    _fresh = False

    @property
    def store(self):
        if not hasattr(self, '_store'):
            self._store = {
                key: value
                for key, value
                in default_settings.__dict__.items()
                if key.isupper()
            }
        return self._store

    def keys(self):
        return self.store.keys()

    def values(self):
        return self.store.values()

    def get(self, key, default=None, cast=None):
        data = self.store.get(key, default)
        if cast:
            data = converters.get(cast)(data)
        return data

    def get_fresh(self, key, default=None, cast=None):
        self.execute_loaders(key=key)
        return self.get(key, default=default, cast=cast)

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def as_bool(self, key):
        return self.get(key, cast='@bool')

    def as_int(self, key):
        return self.get(key, cast='@int')

    def as_float(self, key):
        return self.get(key, cast='@float')

    def as_json(self, key):
        return self.get(key, cast='@json')

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger()
        return self._logger

    @property
    def loaded_namespaces(self):
        if not hasattr(self, '_loaded_namespaces'):
            self._loaded_namespaces = []
        return self._loaded_namespaces

    @loaded_namespaces.setter
    def loaded_namespaces(self, value):
        self._loaded_namespaces = value

    @property
    def loaded_by_loaders(self):
        if not hasattr(self, '_loaded_by_loaders'):
            self._loaded_by_loaders = {}
        return self._loaded_by_loaders

    @contextmanager
    def using_namespace(self, namespace, clean=True):
        try:
            self.namespace(namespace, clean=clean)
            yield
        finally:
            if namespace != self.DYNACONF_NAMESPACE:
                del self.loaded_namespaces[-1]
            self.namespace(self.current_namespace, clean=clean)

    @contextmanager
    def fresh(self):
        self._fresh = True
        yield
        self._fresh = False

    @property
    def current_namespace(self):
        try:
            return self.loaded_namespaces[-1]
        except IndexError:
            return self.DYNACONF_NAMESPACE

    @property
    def settings_module(self):
        if not hasattr(self, 'SETTINGS_MODULE'):
            if not hasattr(self, 'ENVIRONMENT_VARIABLE'):
                ENVIRONMENT_VARIABLE = default_settings.ENVVAR_FOR_DYNACONF
            settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
            self.SETTINGS_MODULE = settings_module
            self.ENVIRONMENT_VARIABLE = ENVIRONMENT_VARIABLE
        return self.SETTINGS_MODULE

    def namespace(self, namespace=None, clean=True):
        namespace = namespace or self.DYNACONF_NAMESPACE

        if namespace != self.DYNACONF_NAMESPACE:
            self.loaded_namespaces.append(namespace)
        else:
            self.loaded_namespaces = []

        if not isinstance(namespace, basestring):
            raise AttributeError('namespace should be a string')
        if "_" in namespace:
            raise AttributeError('namespace should not contains _')
        if clean:
            self.clean(namespace=namespace)
        self.execute_loaders(namespace=namespace)

    def clean(self, namespace=None, silent=None):
        silent = silent or self.DYNACONF_SILENT_ERRORS
        namespace = namespace or self.DYNACONF_NAMESPACE
        for loader in self.loaders:
            loader.clean(self, namespace, silent=silent)

    def unset(self, key):
        delattr(self, key)
        self.store.pop(key, None)

    def set(self, key, value):
        setattr(self, key.upper(), value)
        self.store[key.upper()] = value

    @property
    def loaders(self):
        if not hasattr(self, '_loaders'):
            self._loaders = []
            loaders = self.LOADERS_FOR_DYNACONF
            for loader_module_name in loaders:
                try:
                    loader = importlib.import_module(loader_module_name)
                except ImportError:
                    loader = self.import_from_filename(loader_module_name)
                self._loaders.append(loader)
        return self._loaders

    def reload(self, namespace=None, silent=None):
        self.execute_loaders(namespace, silent)

    def execute_loaders(self, namespace=None, silent=None, key=None):
        default_loader(self)
        module_loader(self)
        silent = silent or self.DYNACONF_SILENT_ERRORS
        for loader in self.loaders:
            loader.load(self, namespace, silent=silent, key=key)


class Settings(BaseSettings):

    def __init__(self, settings_module):
        self.SETTINGS_MODULE = settings_module
        self.execute_loaders()

    def import_from_filename(self, filename, silent=False):
        mod = types.ModuleType('config')
        mod.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(
                    compile(config_file.read(), filename, 'exec'),
                    mod.__dict__
                )
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        return mod


class UserSettingsHolder(BaseSettings):
    """
    Holder for user configured settings.
    """
    # SETTINGS_MODULE doesn't make much sense in the manually configured
    # (standalone) case.
    SETTINGS_MODULE = None

    def __init__(self, default_settings):
        """
        Requests for configuration variables not in this class are satisfied
        from the module specified in default_settings (if possible).
        """
        self.__dict__['_deleted'] = set()
        self.default_settings = default_settings
        self._store = {
            key: value
            for key, value
            in default_settings.__dict__.items()
            if key.isupper()
        }
        self.execute_loaders()

    def __getattr__(self, name):
        if name in self._deleted:
            raise AttributeError
        return getattr(self.default_settings, name)

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        super(UserSettingsHolder, self).__setattr__(name, value)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super(UserSettingsHolder, self).__delattr__(name)

    def __dir__(self):
        return list(self.__dict__) + dir(self.default_settings)

    def is_overridden(self, setting):
        deleted = (setting in self._deleted)
        set_locally = (setting in self.__dict__)
        set_on_default = getattr(
            self.default_settings,
            'is_overridden',
            lambda s: False
        )(setting)
        return (deleted or set_locally or set_on_default)

settings = LazySettings()
