# coding: utf-8
import errno
import importlib
import logging
from contextlib import contextmanager

import os
import sys
import types
from six import string_types

from dynaconf import default_settings
from dynaconf.loaders import default_loader, module_loader, module_cleaner
from dynaconf.loaders import yaml_loader
from dynaconf.transformator import TransformatorList
from dynaconf.utils.functional import LazyObject, empty
from dynaconf.utils.parse_conf import converters, parse_conf_data
from dynaconf.validator import ValidatorList


class LazySettings(LazyObject):
    """
    When you do:
    >>> from dynaconf import settings
    a LazySettings is imported and is initialized with only default_settings.
    When you first access a value, this will be set up using either a
    defined module in DYNACONF_SETTINGS environment variable.

    >>> settings.SETTINGS_MODULE
    Or when you call
    >>> settings.configure(settings_module='/tmp/settings.py')
    You can define in your settings module a list of loaders to get values
    from different stores. By default it will try environment variables
    starting with DYNACONF_NAMESPACE (by defaulf "DYNACONF_")

    You can also import this directly and customize it.
    in a file proj/conf.py
    >>> from dynaconf import LazySettings
    >>> config = LazySettings(ENVVAR_FOR_DYNACONF="PROJ_CONF_FILE",
    ...                       DYNACONF_NAMESPACE='PROJ',
    ...                       LOADERS_FOR_DYNACONF=[
    ...                             'dynaconf.loaders.env_loader',
    ...                             'dynaconf.loaders.redis_loader'
    ...                       ])

    save safe values in a settings file
    $ echo "SERVER_IP = '10.10.10.10'" > proj/settings.py

    define where the settings file is
    $ export PROJ_CONF_FILE=proj.settings

    save unsafe values in environment variable
    $ export PROJ_SERVER_PASSWD='super_secret'

    >>> # from proj.conf import config
    >>> print config.SERVER_IP
    >>> print config.SERVER_PASSWD

    and now it reads all variables starting with PROJ_ from envvars
    and all values in a hash called DYNACONF_PROJ in redis
    """

    def __init__(self, **kwargs):
        """
        handle initialization for the customization cases
        :param kwargs: values that overrides default_settings
        """
        for k, v in kwargs.items():
            setattr(default_settings, k.upper(), v)
        super(LazySettings, self).__init__()

    def __getattr__(self, name):
        """Allow getting keys from self.store using dot notation"""
        if self._wrapped is empty:
            self._setup()
        if name in self._wrapped._deleted:  # noqa
            raise AttributeError(
                "Attribute %s was deleted, "
                "or belongs to different namespace" % name
            )
        always_fresh = self._wrapped.DYNACONF_ALWAYS_FRESH_VARS
        if self._wrapped._fresh or name in always_fresh:  # noqa
            return self._wrapped.get_fresh(name)
        return getattr(self._wrapped, name)

    def __call__(self, *args, **kwargs):
        """Allow direct call of settings('val')
        in place of settings.get('val')
        """
        return self.get(*args, **kwargs)

    def _setup(self):
        """Initial setup, run once."""
        environment_variable = default_settings.ENVVAR_FOR_DYNACONF
        settings_module = os.environ.get(environment_variable)
        self._wrapped = Settings(settings_module=settings_module)

    def configure(self, settings_module=None, **kwargs):
        """
        Allows user to reconfigure settings object passing a new settings
        module or separated kwargs
        :param settings_module:
        :param kwargs:
        """
        self._wrapped = Settings(settings_module=settings_module, **kwargs)

    @property
    def configured(self):
        """If wrapped is configured"""
        return self._wrapped is not empty


class Settings:
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
    env = os.environ

    SETTINGS_MODULE = None
    DYNACONF_NAMESPACE = None
    ENVVAR_FOR_DYNACONF = None
    REDIS_FOR_DYNACONF = None
    LOADERS_FOR_DYNACONF = None
    DYNACONF_SILENT_ERRORS = None
    DYNACONF_ALWAYS_FRESH_VARS = None

    def __init__(self, settings_module=None, **kwargs):  # pragma: no cover
        """Execute loaders and custom initialization"""
        if settings_module:
            self.set('SETTINGS_MODULE', settings_module)
        self.execute_loaders()
        for key, value in kwargs.items():
            self.set(key, value)

    def __call__(self, *args, **kwargs):
        """Allow direct call of settings('val')
        in place of settings.get('val')
        """
        return self.get(*args, **kwargs)

    def __setattr__(self, name, value):
        """Allow settings.FOO = 'value' and deal with _deleted"""
        self._deleted.discard(name)
        super(Settings, self).__setattr__(name, value)

    def __delattr__(self, name):
        """stores reference in _deleted for proper error management"""
        self._deleted.add(name)
        if hasattr(self, name):
            super(Settings, self).__delattr__(name)

    def __getitem__(self, item):
        """Allow getting variables as dict keys settings['KEY']"""
        value = self.get(item)
        if not value:
            raise KeyError('{0} does not exists'.format(item))
        return value

    def __setitem__(self, key, value):
        """Allow settings['KEY'] = 'value'"""
        self.set(key, value)

    @property
    def store(self):
        """Get or create internal storage"""
        if not self._store:
            self._store = {
                key: value
                for key, value
                in default_settings.__dict__.items()
                if key.isupper()
            }
        return self._store

    def keys(self):
        """Redirects to store object"""
        return self.store.keys()

    def values(self):
        """Redirects to store object"""
        return self.store.values()

    def get(self, key, default=None, cast=None, fresh=False):
        """
        Get a value from settings store, this is the prefered way to access
        >>> from dynaconf import settings
        >>> settings.get('KEY')
        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :param fresh: Should reload from loaders store before access?
        :return: The value if found, default or None
        """
        key = key.upper()
        if key in self._deleted:
            return default
        if fresh or self._fresh or key in self.DYNACONF_ALWAYS_FRESH_VARS:
            self.execute_loaders(key=key)
        data = self.store.get(key, default)
        if cast:
            data = converters.get(cast)(data)
        return data

    def exists(self, key, fresh=False):
        """Check if key exists
        NOTE: Must implement regex pattern here!!"""
        key = key.upper()
        if key in self._deleted:
            return False
        if fresh or self._fresh or key in self.DYNACONF_ALWAYS_FRESH_VARS:
            self.execute_loaders(key=key)
        return key in self.store

    def get_fresh(self, key, default=None, cast=None):
        """
        This is a shortcut to get(key, fresh=True). always reload from
        loaders store before getting the var.
        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :return: The value if found, default or None
        """
        return self.get(key, default=default, cast=cast, fresh=True)

    def get_env(self, key, default=None, cast=None):
        """
        Get value from environment variable using os.environ.get
        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :return: The value if found, default or None
        """
        key = key.upper()
        data = self.env.get(key, default)
        if data and cast:
            data = converters.get(cast)(data)
        return data

    def exists_in_env(self, key):
        """Return True if env variable is exported"""
        return key.upper() in self.env

    def as_bool(self, key):
        """Partial method for get with cast"""
        return self.get(key, cast='@bool')

    def as_int(self, key):
        """Partial method for get with cast"""
        return self.get(key, cast='@int')

    def as_float(self, key):
        """Partial method for get with cast"""
        return self.get(key, cast='@float')

    def as_json(self, key):
        """Partial method for get with cast"""
        return self.get(key, cast='@json')

    @property
    def logger(self):  # pragma: no cover
        """Get or create inner logger"""
        if not self._logger:
            self._logger = logging.getLogger()
        return self._logger

    @property
    def loaded_namespaces(self):
        """Get or create internal loaded namespaces list"""
        if not self._loaded_namespaces:
            self._loaded_namespaces = []
        return self._loaded_namespaces

    @loaded_namespaces.setter
    def loaded_namespaces(self, value):
        """Setter for namespace list"""
        self._loaded_namespaces = value

    @property
    def loaded_by_loaders(self):
        """Gets the internal mapping of LOADER -> values"""
        return self._loaded_by_loaders

    @contextmanager
    def using_namespace(self, namespace, clean=True):
        """
        This context manager allows the contextual use of a different namespace
        Example:
        $ export DYNACONF_MESSAGE='This is in DYNACONF namespace'
        $ export OTHER_MESSAGE='This is in OTHER namespace'
        >>> from dynaconf import settings
        >>> print settings.MESSAGE
        'This is in DYNACONF namespace'
        >>> with settings.using_namespace('OTHER'):
        ...    print settings.MESSAGE
        'This is in OTHER namespace'
        >>> print settings.MESSAGE
        'This is in DYNACONF namespace'

        :param namespace: Upper case name of namespace without any _
        :param clean: If preloaded vars should be cleaned
        :return: context
        """
        try:
            self.namespace(namespace, clean=clean)
            yield
        finally:
            if namespace != self.DYNACONF_NAMESPACE:
                del self.loaded_namespaces[-1]
            self.namespace(self.current_namespace, clean=clean)

    @contextmanager
    def fresh(self):
        """
        this context manager force the load of a key direct from the store
        $ export DYNACONF_VALUE='Original'
        >>> from dynaconf import settings
        >>> print settings.VALUE
        'Original'
        $ export DYNACONF_VALUE='Changed Value'
        >>> print settings.VALUE  # will not be reloaded from env vars
        'Original
        >>> with settings.fresh(): # inside this context all is reloaded
        ...    print settings.VALUE
        'Changed Value'

        an alternative is using settings.get_fresh(key)

        :return: context
        """
        self._fresh = True
        yield
        self._fresh = False

    @property
    def current_namespace(self):
        """Return the current active namespace"""
        try:
            return self.loaded_namespaces[-1]
        except IndexError:
            return self.DYNACONF_NAMESPACE

    @property
    def settings_module(self):
        """Gets or initialize SETTINGS_MODULE variable"""
        if not self.SETTINGS_MODULE:
            environment_variable = getattr(
                self,
                'ENVIRONMENT_VARIABLE',
                default_settings.ENVVAR_FOR_DYNACONF
            )
            settings_module = os.environ.get(
                environment_variable,
                default_settings.SETTINGS_MODULE_FOR_DYNACONF
            )
            self.set('SETTINGS_MODULE', settings_module)
            self.set('ENVIRONMENT_VARIABLE', environment_variable)

        return self.SETTINGS_MODULE

    def namespace(self, namespace=None, clean=True):
        """
        Used to interactively change the namespace
        $ export DYNACONF_MESSAGE='This is in DYNACONF namespace'
        $ export OTHER_MESSAGE='This is in OTHER namespace'
        >>> from dynaconf import settings
        >>> print settings.MESSAGE
        'This is in DYNACONF namespace'
        >>> settings.namespace('OTHER')  # loaded vars from OTHER*
        >>> print settings.MESSAGE
        'This is in OTHER namespace'
        >>> settings.namespace()  # without params back to default
        >>> print settings.MESSAGE
        'This is in DYNACONF namespace'

        :param namespace: Upper case namespace name without any _
        :param clean: Should clean preloaded vars?
        :return: None
        """
        namespace = namespace or self.DYNACONF_NAMESPACE

        if namespace != self.DYNACONF_NAMESPACE:
            self.loaded_namespaces.append(namespace)
        else:
            self.loaded_namespaces = []

        if not isinstance(namespace, string_types):
            raise AttributeError('namespace should be a string')
        if "_" in namespace:
            raise AttributeError('namespace should not contains _')
        if clean:
            self.clean(namespace=namespace)
        self.execute_loaders(namespace=namespace)

    def clean(self, namespace=None, silent=None):
        """Clean all loaded values to reload when switching namespaces"""
        silent = silent or self.DYNACONF_SILENT_ERRORS
        namespace = namespace or self.DYNACONF_NAMESPACE
        for loader in self.loaders:
            loader.clean(self, namespace, silent=silent)
        yaml_loader.clean(self, namespace, silent=silent)
        module_cleaner(self, namespace, silent=silent)

    def unset(self, key):
        """Unset on all references"""
        key = key.strip().upper()
        delattr(self, key)
        self.store.pop(key, None)

    def unset_all(self, keys):  # pragma: no cover
        """Unset based on a list of keys"""
        for key in keys:
            self.unset(key)

    def set(self, key, value, loader_identifier=None):
        """Set a value storing references for the loader"""
        value = parse_conf_data(value)
        key = key.strip().upper()
        setattr(self, key, value)
        self.store[key] = value

        if loader_identifier and loader_identifier in self.loaded_by_loaders:
            self.loaded_by_loaders[loader_identifier][key] = value
        elif loader_identifier:
            self.loaded_by_loaders[loader_identifier] = {key: value}

    def update(self, data=None, loader_identifier=None, **kwargs):
        """
        Update values in the current settings object without saving in stores
        >>> from dynaconf import settings
        >>> print settings.NAME
        'Bruno'
        >>> settings.update({'NAME': 'John'}, other_value=1)
        >>> print settings.NAME
        'John'
        >>> print settings.OTHER_VALUE
        1

        :param data: Data to be updated
        :param loader_identifier: Only to be used by custom loaders
        :param kwargs: extra values to update
        :return: None
        """
        data = data or {}
        data.update(kwargs)
        for key, value in data.items():
            self.set(key, value)
        if loader_identifier:
            self.loaded_by_loaders[loader_identifier] = data

    @property
    def loaders(self):  # pragma: no cover
        """Return available loaders"""
        if not self._loaders:
            for loader_module_name in self.LOADERS_FOR_DYNACONF:
                try:
                    loader = importlib.import_module(loader_module_name)
                except ImportError:
                    loader = self.import_from_filename(loader_module_name)
                self._loaders.append(loader)
        return self._loaders

    def reload(self, namespace=None, silent=None):  # pragma: no cover
        """Execute all loaders"""
        self.execute_loaders(namespace, silent)

    def execute_loaders(self, namespace=None, silent=None, key=None):
        """Execute all internal and registered loaders"""
        default_loader(self)
        module_loader(self, namespace=namespace)
        if self.exists('YAML'):
            yaml_loader.load(
                self, namespace=namespace, filename=self.get('YAML')
            )
        silent = silent or self.DYNACONF_SILENT_ERRORS
        for loader in self.loaders:
            loader.load(self, namespace, silent=silent, key=key)

    @staticmethod
    def import_from_filename(filename, silent=False):  # pragma: no cover
        """If settings_module is a path use this."""
        if not filename.endswith('.py'):
            filename = '{0}.py'.format(filename)

        if filename == default_settings.SETTINGS_MODULE_FOR_DYNACONF:
            silent = True
        mod = types.ModuleType('config')
        mod.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(
                    compile(config_file.read(), filename, 'exec'),
                    mod.__dict__
                )
        except IOError as e:
            e.strerror = (
                'Unable to load configuration file (%s %s)\n'
            ) % (e.strerror, filename)
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return
            sys.stderr.write(e.strerror)
        return mod

    def path_for(self, *args):
        """Path containing project_root"""
        if args and args[0].startswith('/'):
            return os.path.join(*args)
        return os.path.join(self.PROJECT_ROOT, *args)

    @property
    def validators(self):
        """Gets or creates validator wrapper"""
        if not hasattr(self, '_validators'):
            self._validators = ValidatorList(self)
        return self._validators

    @property
    def transformators(self):
        """Gets or creates transformator wrapper"""
        if not hasattr(self, '_transformators'):
            self._transformators = TransformatorList(self)
        return self._transformators
