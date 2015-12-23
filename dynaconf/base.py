import os
import types
import errno
import logging
import importlib
from contextlib import contextmanager
from dynaconf import default_settings
from dynaconf.utils.parse_conf import converters
from dynaconf.utils.functional import LazyObject, empty
from dynaconf.loaders import default_loader, module_loader


class LazySettings(LazyObject):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(default_settings, k.upper(), v)
        super(LazySettings, self).__init__()

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup(name)
        if name in self._wrapped._deleted:  # noqa
            raise AttributeError("Attribute %s was deleted" % name)
        always_fresh = self._wrapped.DYNACONF_ALWAYS_FRESH_VARS
        if self._wrapped._fresh or name in always_fresh:  # noqa
            return self._wrapped.get_fresh(name)
        return getattr(self._wrapped, name)

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def _setup(self, name=None):
        environment_variable = default_settings.ENVVAR_FOR_DYNACONF
        settings_module = os.environ.get(environment_variable)
        self._wrapped = Settings(settings_module=settings_module)

    def configure(self, settings_module=None, **kwargs):
        self._wrapped = Settings(settings_module=settings_module, **kwargs)

    @property
    def configured(self):
        return self._wrapped is not empty


class Settings(object):
    """
    Common logic for settings whether set by a module or by the user.
    """
    _logger = None
    _fresh = False
    _loaded_namespaces = []
    _deleted = set()
    _store = {}
    _loaded_by_loaders = {}
    _loaders = []

    SETTINGS_MODULE = None
    DYNACONF_NAMESPACE = None
    ENVVAR_FOR_DYNACONF = None
    REDIS_FOR_DYNACONF = None
    LOADERS_FOR_DYNACONF = None
    DYNACONF_SILENT_ERRORS = None
    DYNACONF_ALWAYS_FRESH_VARS = None

    def __init__(self, settings_module=None, **kwargs):
        if settings_module:
            self.set('SETTINGS_MODULE', settings_module)
        self.execute_loaders()
        for key, value in kwargs.items():
            self.set(key, value)

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        super(Settings, self).__setattr__(name, value)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super(Settings, self).__delattr__(name)

    @property
    def store(self):
        if not self._store:
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

    def get(self, key, default=None, cast=None, fresh=False):
        if fresh or self._fresh or key in self.DYNACONF_ALWAYS_FRESH_VARS:
            self.execute_loaders(key=key)
        data = self.store.get(key, default)
        if cast:
            data = converters.get(cast)(data)
        return data

    def get_fresh(self, key, default=None, cast=None):
        return self.get(key, default=default, cast=cast, fresh=True)

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
        if not self._logger:
            self._logger = logging.getLogger()
        return self._logger

    @property
    def loaded_namespaces(self):
        if not self._loaded_namespaces:
            self._loaded_namespaces = []
        return self._loaded_namespaces

    @loaded_namespaces.setter
    def loaded_namespaces(self, value):
        self._loaded_namespaces = value

    @property
    def loaded_by_loaders(self):
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
        if not self.SETTINGS_MODULE:
            environment_variable = getattr(
                self,
                'ENVIRONMENT_VARIABLE',
                default_settings.ENVVAR_FOR_DYNACONF
            )
            settings_module = os.environ.get(environment_variable)
            self.set('SETTINGS_MODULE', settings_module)
            self.set('ENVIRONMENT_VARIABLE', environment_variable)
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
        if not self._loaders:
            for loader_module_name in self.LOADERS_FOR_DYNACONF:
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

    @staticmethod
    def import_from_filename(filename, silent=False):
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
