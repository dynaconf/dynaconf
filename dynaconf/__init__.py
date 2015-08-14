"""
Dynamic Settings Loader.

Values will be read from the module specified by the DYNACONF_SETTINGS_MODULE
environment variable;
"""
import os
import importlib
from dynaconf import default_settings
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.conf.exceptions import ImproperlyConfigured
from dynaconf.conf.functional import LazyObject, empty

ENVIRONMENT_VARIABLE = "DYNACONF_SETTINGS_MODULE"


class LazySettings(LazyObject):
    """
    A lazy proxy for either global settings or a custom settings obj
    The user can manually configure settings prior to using them. Otherwise,
    uses the settings module pointed to by DYNACONF_SETTINGS_MODULE.
    """
    def _setup(self, name=None):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has
        not previously configured the settings manually.
        """
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
        return getattr(self._wrapped, name)

    def configure(self, root=None, default_settings=default_settings, **options):
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


class BaseSettings(object):
    """
    Common logic for settings whether set by a module or by the user.
    """
    @property
    def store(self):
        if not hasattr(self, '_store'):
            self._store = {}
        return self._store

    def keys(self):
        return self.store.keys()

    def values(self):
        return self.store.values()

    def get(self, key, default=None):
        return self.store.get(key, default)

    def load_from_envvar_namespace(self, namespace='DYNACONF', silent=True):
        try:
            data = {
                key.partition('_')[-1]: parse_conf_data(data)
                for key, data
                in os.environ.items()
                if key.startswith(namespace)
            }
            for key, value in data.items():
                setattr(self, key, value)
                self.store[key] = value
        except Exception as e:
            if silent:
                return False
            e.message = 'Unable to load config env namespace (%s)' % e.message
            raise


class Settings(BaseSettings):
    def __init__(self, settings_module):
        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module

        mod = importlib.import_module(self.SETTINGS_MODULE)

        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)
                self.store[setting] = setting_value

        if not hasattr(self, 'PROJECT_ROOT'):
            self.PROJECT_ROOT = os.path.realpath(
                os.path.dirname(os.path.abspath(self.SETTINGS_MODULE))
            )

        self.load_from_envvar_namespace()

    def is_overridden(self, setting):
        return setting in self._explicit_settings


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
        self.load_from_envvar_namespace()

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
