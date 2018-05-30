# coding: utf-8
import os
import importlib
from contextlib import contextmanager

from six import string_types

from dynaconf import default_settings
from dynaconf.loaders import (
    default_loader,
    settings_loader,
    yaml_loader,
    enable_external_loaders
)
from dynaconf.utils.functional import LazyObject, empty
from dynaconf.utils.parse_conf import converters, parse_conf_data, true_values
from dynaconf.utils import BANNER, compat_kwargs, raw_logger
from dynaconf.validator import ValidatorList
from dynaconf.utils.boxing import DynaBox


class LazySettings(LazyObject):
    """When you do::

        >>> from dynaconf import settings

    a LazySettings is imported and is initialized with only default_settings.

    Then when you first access a value, this will be set up and loaders will
    be executes looking for default config files or the file defined in
    SETTINGS_MODULE_FOR_DYNACONF variable::

        >>> settings.SETTINGS_MODULE

    Or when you call::

        >>> settings.configure(settings_module='/tmp/settings.py')

    You can define in your settings module a list of loaders to get values
    from different stores. By default it will try environment variables
    starting with GLOBAL_ENV_FOR_DYNACONF (by defaulf `DYNACONF_`)

    You can also import this directly and customize it.
    in a file `proj/conf.py`::

        >>> from dynaconf import LazySettings
        >>> config = LazySettings(ENV_FOR_DYNACONF='PROJ',
        ...                       LOADERS_FOR_DYNACONF=[
        ...                             'dynaconf.loaders.env_loader',
        ...                             'dynaconf.loaders.redis_loader'
        ...                       ])

    save common values in a settings file::

        $ echo "SERVER_IP = '10.10.10.10'" > proj/settings.py

    or use `.toml|.yaml|.ini|.json`

    save sensitive values in .secrets.{py|toml|yaml|ini|json}
    or export as DYNACONF global environment variable::

        $ export DYNACONF_SERVER_PASSWD='super_secret'

        >>> # from proj.conf import config
        >>> print config.SERVER_IP
        >>> print config.SERVER_PASSWD

    and now it reads all variables starting with `DYNACONF_` from envvars
    and all values in a hash called DYNACONF_PROJ in redis
    """

    def __init__(self, **kwargs):
        """
        handle initialization for the customization cases

        :param kwargs: values that overrides default_settings
        """
        compat_kwargs(kwargs)
        self._kwargs = kwargs
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
                "or belongs to different env" % name
            )
        if (
            name.isupper() and
            (self._wrapped._fresh or
             name in self._wrapped.FRESH_VARS_FOR_DYNACONF) and
            name not in dir(default_settings)
        ):
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
        self._wrapped = Settings(
            settings_module=settings_module, **self._kwargs
        )

    def configure(self, settings_module=None, **kwargs):
        """
        Allows user to reconfigure settings object passing a new settings
        module or separated kwargs

        :param settings_module: defines the setttings file
        :param kwargs:  override default settings
        """
        compat_kwargs(kwargs)
        kwargs.update(self._kwargs)
        self._wrapped = Settings(settings_module=settings_module, **kwargs)

    @property
    def configured(self):
        """If wrapped is configured"""
        return self._wrapped is not empty


class Settings(object):
    """
    Common logic for settings whether set by a module or by the user.
    """

    dynaconf_banner = BANNER

    def __init__(self, settings_module=None, **kwargs):  # pragma: no cover
        """Execute loaders and custom initialization

        :param settings_module: defines the setttings file
        :param kwargs:  override default settings
        """
        self._logger = None
        self._fresh = False
        self._loaded_envs = []
        self._deleted = set()
        self._store = {}
        self._loaded_by_loaders = {}
        self._loaders = []
        self._defaults = {}
        self.environ = os.environ
        self.SETTINGS_MODULE = None
        self._not_installed_warnings = []

        compat_kwargs(kwargs)
        if settings_module:
            self.set('SETTINGS_MODULE', settings_module)
        for key, value in kwargs.items():
            self.set(key, value)
        # execute loaders only after setting defaults got from kwargs
        self._defaults = kwargs
        self.execute_loaders()

    def __call__(self, *args, **kwargs):
        """Allow direct call of `settings('val')`
        in place of `settings.get('val')`
        """
        return self.get(*args, **kwargs)

    def __setattr__(self, name, value):
        """Allow `settings.FOO = 'value'` and deal with `_deleted`"""
        try:
            self._deleted.discard(name)
        except AttributeError:
            pass

        super(Settings, self).__setattr__(name, value)

    def __delattr__(self, name):
        """stores reference in `_deleted` for proper error management"""
        self._deleted.add(name)
        if hasattr(self, name):
            super(Settings, self).__delattr__(name)

    def __getitem__(self, item):
        """Allow getting variables as dict keys `settings['KEY']`"""
        value = self.get(item)
        if not value:
            raise KeyError('{0} does not exists'.format(item))
        return value

    def __setitem__(self, key, value):
        """Allow `settings['KEY'] = 'value'`"""
        self.set(key, value)

    @property
    def store(self):
        """Gets internal storage"""
        return self._store

    def keys(self):
        """Redirects to store object"""
        return self.store.keys()

    def values(self):
        """Redirects to store object"""
        return self.store.values()

    def get(self, key, default=None, cast=None, fresh=False):
        """
        Get a value from settings store, this is the prefered way to access::

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

        if (
            (fresh or self._fresh or key in self.FRESH_VARS_FOR_DYNACONF) and
            key not in dir(default_settings)
        ):
            self.unset(key)
            self.execute_loaders(key=key)
        data = self.store.get(key, default)
        if cast:
            data = converters.get(cast)(data)
        return data

    def exists(self, key, fresh=False):
        """Check if key exists

        :param key: the name of setting variable
        :param fresh: if key should be taken from source direclty
        :return: Boolean
        """
        key = key.upper()
        if key in self._deleted:
            return False
        if (
            (fresh or self._fresh or key in self.FRESH_VARS_FOR_DYNACONF) and
            key not in dir(default_settings)
        ):
            self.execute_loaders(key=key)
        return key in self.store

    def get_fresh(self, key, default=None, cast=None):
        """This is a shortcut to `get(key, fresh=True)`. always reload from
        loaders store before getting the var.

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :return: The value if found, default or None
        """
        return self.get(key, default=default, cast=cast, fresh=True)

    def get_environ(self, key, default=None, cast=None):
        """Get value from environment variable using os.environ.get

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
         or cast must be true to use cast inference
        :return: The value if found, default or None
        """
        key = key.upper()
        data = self.environ.get(key, default)
        if data:
            if cast in converters:
                data = converters.get(cast)(data)
            if cast is True:
                data = parse_conf_data(data, tomlfy=True)
        return data

    def exists_in_environ(self, key):
        """Return True if env variable is exported"""
        return key.upper() in self.environ

    def as_bool(self, key):
        """Partial method for get with bool cast"""
        return self.get(key, cast='@bool')

    def as_int(self, key):
        """Partial method for get with int cast"""
        return self.get(key, cast='@int')

    def as_float(self, key):
        """Partial method for get with float cast"""
        return self.get(key, cast='@float')

    def as_json(self, key):
        """Partial method for get with json cast"""
        return self.get(key, cast='@json')

    @property
    def logger(self):  # pragma: no cover
        """Get or create inner logger"""
        return raw_logger()

    @property
    def loaded_envs(self):
        """Get or create internal loaded envs list"""
        if not self._loaded_envs:
            self._loaded_envs = []
        return self._loaded_envs

    # compat
    loaded_namespaces = loaded_envs

    @loaded_envs.setter
    def loaded_envs(self, value):
        """Setter for env list"""
        self._loaded_envs = value

    @property
    def loaded_by_loaders(self):
        """Gets the internal mapping of LOADER -> values"""
        return self._loaded_by_loaders

    @contextmanager
    def using_env(self, env, clean=True, silent=True, filename=None):
        """
        This context manager allows the contextual use of a different env
        Example of settings.toml::

            [development]
            message = 'This is in dev'
            [other]
            message = 'this is in other env'

        Program::

            >>> from dynaconf import settings
            >>> print settings.MESSAGE
            'This is in dev'
            >>> with settings.using_env('OTHER'):
            ...    print settings.MESSAGE
            'this is in other env'

        :param env: Upper case name of env without any _
        :param clean: If preloaded vars should be cleaned
        :param silent: Silence errors
        :param filename: Custom filename to load (optional)
        :return: context
        """
        try:
            self.setenv(env, clean=clean, silent=silent, filename=filename)
            self.logger.debug("In env: %s", env)
            yield
        finally:
            if env.lower() != self.ENV_FOR_DYNACONF.lower():
                del self.loaded_envs[-1]
            self.logger.debug("Out env: %s", env)
            self.setenv(self.current_env, clean=clean, filename=filename)

    # compat
    using_namespace = using_env

    @contextmanager
    def fresh(self):
        """
        this context manager force the load of a key direct from the store::

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

        an alternative is using `settings.get_fresh(key)`

        :return: context
        """

        self._fresh = True
        yield
        self._fresh = False

    @property
    def current_env(self):
        """Return the current active env"""
        try:
            return self.loaded_envs[-1]
        except IndexError:
            return self.ENV_FOR_DYNACONF
    # compat
    current_namespace = current_env

    @property
    def settings_module(self):
        """Gets SETTINGS_MODULE variable"""
        settings_module = os.environ.get(
            self.ENVVAR_FOR_DYNACONF,
            self.SETTINGS_MODULE_FOR_DYNACONF
        )
        if settings_module != self.SETTINGS_MODULE:
            self.set('SETTINGS_MODULE', settings_module)
        return self.SETTINGS_MODULE

    def setenv(self, env=None, clean=True, silent=True, filename=None):
        """Used to interactively change the env
        Example of settings.toml::

            [development]
            message = 'This is in dev'
            [other]
            message = 'this is in other env'

        Program::

            >>> from dynaconf import settings
            >>> print settings.MESSAGE
            'This is in dev'
            >>> with settings.using_env('OTHER'):
            ...    print settings.MESSAGE
            'this is in other env'

        :param env: Upper case name of env without any _
        :param clean: If preloaded vars should be cleaned
        :param silent: Silence errors
        :param filename: Custom filename to load (optional)
        :return: context
        """
        env = env or self.ENV_FOR_DYNACONF

        if not isinstance(env, string_types):
            raise AttributeError('env should be a string')
        if "_" in env:
            raise AttributeError('env should not contains _')

        self.logger.debug("env switching to: %s", env)

        env = env.upper()

        if env != self.ENV_FOR_DYNACONF:
            self.loaded_envs.append(env)
        else:
            self.loaded_envs = []

        if clean:
            self.clean(env=env)
        self.execute_loaders(env=env, silent=silent, filename=filename)

    # compat
    namespace = setenv

    def clean(self, *args, **kwargs):
        """Clean all loaded values to reload when switching envs"""
        for key in list(self.store.keys()):
            self.unset(key)

    def unset(self, key):
        """Unset on all references

        :param key: The key to be unset
        """
        key = key.strip().upper()
        if key not in dir(default_settings) and key not in self._defaults:
            self.logger.debug('Unset %s', key)
            delattr(self, key)
            self.store.pop(key, None)

    def unset_all(self, keys):  # pragma: no cover
        """Unset based on a list of keys

        :param keys: a list of keys
        """
        for key in keys:
            self.unset(key)

    def set(self, key, value, loader_identifier=None, tomlfy=False):
        """Set a value storing references for the loader

        :param key: The key to store
        :param value: The value to store
        :param loader_identifier: Optional loader name e.g: toml, yaml etc.
        :param tomlfy: Bool define if value is parsed by toml (defaults False)
        """
        value = parse_conf_data(value, tomlfy=tomlfy)
        if isinstance(value, dict):
            value = DynaBox(value, box_it_up=True)

        key = key.strip().upper()
        setattr(self, key, value)
        self.store[key] = value
        self._deleted.discard(key)

        # set loader identifiers so cleaners know which keys to clean
        if loader_identifier and loader_identifier in self.loaded_by_loaders:
            self.loaded_by_loaders[loader_identifier][key] = value
        elif loader_identifier:
            self.loaded_by_loaders[loader_identifier] = {key: value}
        elif loader_identifier is None:
            # if .set is called without loader identifier it becomes
            # a default value and goes away only when explicitly unset
            self._defaults[key] = value

    def update(self, data=None, loader_identifier=None,
               tomlfy=False, **kwargs):
        """
        Update values in the current settings object without saving in stores::

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
        :param tomlfy: Bool define if value is parsed by toml (defaults False)
        :param kwargs: extra values to update
        :return: None
        """
        data = data or {}
        data.update(kwargs)
        for key, value in data.items():
            self.set(key, value, loader_identifier=loader_identifier,
                     tomlfy=tomlfy)

    @property
    def loaders(self):  # pragma: no cover
        """Return available loaders"""
        if self.LOADERS_FOR_DYNACONF in (None, 0, "0", "false", False):
            self.logger.info('No loader defined')
            return []

        if not self._loaders:
            for loader_module_name in self.LOADERS_FOR_DYNACONF:
                loader = importlib.import_module(loader_module_name)
                self._loaders.append(loader)

        return self._loaders

    def reload(self, env=None, silent=None):  # pragma: no cover
        """Clean end Execute all loaders"""
        self.clean()
        self.execute_loaders(env, silent)

    def execute_loaders(self, env=None, silent=None, key=None, filename=None):
        """Execute all internal and registered loaders

        :param env: The environment to load
        :param silent: If loading erros is silenced
        :param key: if provided load a single key
        :param filename: optinal custom filename to load
        """
        if key is None:
            default_loader(self, self._defaults)
        silent = silent or self.SILENT_ERRORS_FOR_DYNACONF
        settings_loader(self, env=env, silent=silent, key=key,
                        filename=filename)
        self.load_extra_yaml(env, silent, key)  # DEPRECATED
        enable_external_loaders(self)
        for loader in self.loaders:
            self.logger.debug('Dynaconf executing: %s', loader.__name__)
            loader.load(self, env, silent=silent, key=key)

    def load_extra_yaml(self, env, silent, key):
        """This is deprecated, kept for compat

        .. deprecated:: 1.0.0
            Use multiple settings files instead.
        """
        if self.get('YAML') is not None:
            self.logger.warning(
                "The use of YAML var is deprecated, please define multiple "
                "filepaths instead: "
                "e.g: SETTINGS_MODULE_FOR_DYNACONF = "
                "'settings.py,settings.yaml,settings.toml'"
            )
            yaml_loader.load(
                self, env=env,
                filename=self.get('YAML'),
                silent=silent,
                key=key
            )

    def path_for(self, *args):
        """Path containing PROJECT_ROOT_FOR_DYNACONF"""
        if args and args[0].startswith('/'):
            return os.path.join(*args)
        return os.path.join(self.PROJECT_ROOT_FOR_DYNACONF, *args)

    @property
    def validators(self):
        """Gets or creates validator wrapper"""
        if not hasattr(self, '_validators'):
            self._validators = ValidatorList(self)
        return self._validators

    def flag(self, key, env=None):
        """Feature flagging system
        write flags to redis
        $ dynaconf write redis -s DASHBOARD=1 -e premiumuser
        meaning: Any premium user has DASHBOARD feature enabled

        In your program do::

            # premium user has access to dashboard?
            >>> if settings.flag('dashboard', 'premiumuser'):
            ...     activate_dashboard()

        The value is ensured to be loaded fresh from redis server

        It also works with file settings but the recommended is redis
        as the data can be loaded once it is updated.

        :param key: The flag name
        :param env: The env to look for
        """
        env = env or self.GLOBAL_ENV_FOR_DYNACONF
        with self.using_env(env):
            value = self.get_fresh(key)
            return value is True or value in true_values
