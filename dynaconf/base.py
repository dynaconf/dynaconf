import glob
import importlib
import inspect
import os
import warnings
from contextlib import contextmanager
from contextlib import suppress

from dynaconf import default_settings
from dynaconf.loaders import default_loader
from dynaconf.loaders import enable_external_loaders
from dynaconf.loaders import env_loader
from dynaconf.loaders import py_loader
from dynaconf.loaders import settings_loader
from dynaconf.loaders import yaml_loader
from dynaconf.utils import BANNER
from dynaconf.utils import compat_kwargs
from dynaconf.utils import ensure_a_list
from dynaconf.utils import missing
from dynaconf.utils import object_merge
from dynaconf.utils import RENAMED_VARS
from dynaconf.utils import upperfy
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.files import find_file
from dynaconf.utils.functional import empty
from dynaconf.utils.functional import LazyObject
from dynaconf.utils.parse_conf import converters
from dynaconf.utils.parse_conf import evaluate_lazy_format
from dynaconf.utils.parse_conf import get_converter
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.utils.parse_conf import true_values
from dynaconf.validator import ValidatorList


class LazySettings(LazyObject):
    """When you do::

        >>> from dynaconf import Dynaconf
        >>> settings = Dynaconf(*options)

    a LazySettings is initialized with only default_settings and all the
    parameters passed to *options.

    Then when you first access a value, this will be set up and loaders will
    be executed looking for defined config files or the file defined in
    SETTINGS_FILE_FOR_DYNACONF environment variable::

        $ export SETTINGS_FILE_FOR_DYNACONF=path

        >>> settings.FOO

    Or when you call::

        >>> settings.configure(settings_module='/tmp/settings.py')

    You can define in your settings module a list of loaders to get values
    from different stores. By default it will try environment variables
    starting with ENVVAR_PREFIX_FOR_DYNACONF (by defaulf `DYNACONF_`)

    You can also customize specific parameters.

    Exmaple: `proj/config.py`::

        >>> from dynaconf import Dynaconf
        >>> settings = Dynaconf(
        ...    env='production',
        ...    loaders=[
        ...        'dynaconf.loaders.env_loader',
        ...        'dynaconf.loaders.redis_loader'
        ...    ]
        ... )

    save common values in a settings file::

        $ echo "SERVER_IP = '10.10.10.10'" > proj/settings.py

    or use `.toml|.yaml|.ini|.json`

    save sensitive values in .secrets.{py|toml|yaml|ini|json}
    or export as DYNACONF global environment variable::

        $ export DYNACONF_SERVER_PASSWD='super_secret'

        >>> # from proj.config import settings
        >>> print settings.SERVER_IP
        >>> print settings.SERVER_PASSWD

    and now it reads all variables starting with `DYNACONF_` from envvars
    and all values in a hash called DYNACONF_PROJ in redis
    """

    def __init__(self, **kwargs):
        """
        handle initialization for the customization cases

        :param kwargs: values that overrides default_settings
        """

        self._warn_dynaconf_global_settings = kwargs.pop(
            "warn_dynaconf_global_settings", None
        )  # in 3.0.0 global settings is deprecated

        self.__resolve_config_aliases(kwargs)
        compat_kwargs(kwargs)
        self._kwargs = kwargs
        super(LazySettings, self).__init__()

    def __resolve_config_aliases(self, kwargs):
        """takes aliases for _FOR_DYNACONF configurations

        e.g: ROOT_PATH='/' is transformed into `ROOT_PATH_FOR_DYNACONF`
        """

        mispells = {
            "settings_files": "settings_file",
            "SETTINGS_FILES": "SETTINGS_FILE",
        }
        for mispell, correct in mispells.items():
            if mispell in kwargs:
                kwargs[correct] = kwargs.pop(mispell)

        for_dynaconf_keys = {
            key
            for key in dir(default_settings)
            if key.endswith("_FOR_DYNACONF")
        }
        aliases = {
            key.upper()
            for key in kwargs
            if f"{key.upper()}_FOR_DYNACONF" in for_dynaconf_keys
        }
        for alias in aliases:
            value = kwargs.pop(alias, empty)
            if value is empty:
                value = kwargs.pop(alias.lower())
            kwargs[f"{alias}_FOR_DYNACONF"] = value

    @evaluate_lazy_format
    def __getattr__(self, name):
        """Allow getting keys from self.store using dot notation"""
        if self._wrapped is empty:
            self._setup()
        if name in self._wrapped._deleted:  # noqa
            raise AttributeError(
                f"Attribute {name} was deleted, " "or belongs to different env"
            )

        if name not in RESERVED_ATTRS:
            lowercase_mode = self._kwargs.get(
                "LOWERCASE_READ_FOR_DYNACONF",
                default_settings.LOWERCASE_READ_FOR_DYNACONF,
            )
            if lowercase_mode is True:
                name = name.upper()

        if (
            name.isupper()
            and (
                self._wrapped._fresh
                or name in self._wrapped.FRESH_VARS_FOR_DYNACONF
            )
            and name not in dir(default_settings)
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

        if self._warn_dynaconf_global_settings:
            warnings.warn(
                "Usage of `from dynaconf import settings` is now "
                "DEPRECATED in 3.0.0+. You are encouraged to change it to "
                "your own instance e.g: `settings = Dynaconf(*options)`",
                DeprecationWarning,
            )

        default_settings.reload(self._kwargs.get("load_dotenv"))
        environment_variable = self._kwargs.get(
            "ENVVAR_FOR_DYNACONF", default_settings.ENVVAR_FOR_DYNACONF
        )
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
        default_settings.reload(self._kwargs.get("load_dotenv"))
        environment_var = self._kwargs.get(
            "ENVVAR_FOR_DYNACONF", default_settings.ENVVAR_FOR_DYNACONF
        )
        settings_module = settings_module or os.environ.get(environment_var)
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
        self._fresh = False
        self._loaded_envs = []
        self._loaded_files = []
        self._deleted = set()
        self._store = DynaBox(box_settings=self)
        self._env_cache = {}
        self._loaded_by_loaders = {}
        self._loaders = []
        self._defaults = DynaBox(box_settings=self)
        self.environ = os.environ
        self.SETTINGS_MODULE = None
        self._not_installed_warnings = []
        self._memoized = None

        self.validators = ValidatorList(
            self, validators=kwargs.pop("validators", None)
        )

        compat_kwargs(kwargs)
        if settings_module:
            self.set("SETTINGS_FILE_FOR_DYNACONF", settings_module)
        for key, value in kwargs.items():
            self.set(key, value)
        # execute loaders only after setting defaults got from kwargs
        self._defaults = kwargs
        self.execute_loaders()

        self.validators.validate()

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

    def __contains__(self, item):
        "Respond to `item in settings`"
        return item.upper() in self.store or item.lower() in self.store

    def __getitem__(self, item):
        """Allow getting variables as dict keys `settings['KEY']`"""
        value = self.get(item, default=empty)
        if value is empty:
            raise KeyError(f"{item} does not exist")
        return value

    def __setitem__(self, key, value):
        """Allow `settings['KEY'] = 'value'`"""
        self.set(key, value)

    @property
    def store(self):
        """Gets internal storage"""
        return self._store

    def __dir__(self):
        """Enable auto-complete for code editors"""
        return (
            RESERVED_ATTRS
            + [k.lower() for k in self.keys()]
            + list(self.keys())
        )

    def __iter__(self):
        """Redirects to store object"""
        yield from self._store

    def items(self):
        """Redirects to store object"""
        return self._store.items()

    def keys(self):
        """Redirects to store object"""
        return self.store.keys()

    def values(self):
        """Redirects to store object"""
        return self.store.values()

    def setdefault(self, item, default):
        """Returns value if exists or set it as the given default"""
        value = self.get(item, empty)
        if value is empty and default is not empty:
            self.set(
                item,
                default,
                loader_identifier="setdefault",
                tomlfy=True,
                dotted_lookup=True,
            )
            return default
        return value

    def as_dict(self, env=None, internal=False):
        """Returns a dictionary with set key and values.

        :param env: Str env name, default self.current_env `DEVELOPMENT`
        :param internal: bool - should include dynaconf internal vars?
        """
        ctx_mgr = suppress() if env is None else self.using_env(env)
        with ctx_mgr:
            data = self.store.to_dict().copy()
            # if not internal remove internal settings
            if not internal:
                for name in dir(default_settings):
                    data.pop(name, None)
            return data

    to_dict = as_dict  # backwards compatibility

    def _dotted_get(self, dotted_key, default=None, parent=None, **kwargs):
        """
        Perform dotted key lookups and keep track of where we are.
        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param parent: Is there a pre-loaded parent in a nested data?
        """
        split_key = dotted_key.split(".")
        name, keys = split_key[0], split_key[1:]
        result = self.get(name, default=default, parent=parent, **kwargs)

        # If we've reached the end, or parent key not found, then return result
        if not keys or result == default:
            return result

        # If we've still got key elements to traverse, let's do that.
        return self._dotted_get(
            ".".join(keys), default=default, parent=result, **kwargs
        )

    @evaluate_lazy_format
    def get(
        self,
        key,
        default=None,
        cast=None,
        fresh=False,
        dotted_lookup=True,
        parent=None,
    ):
        """
        Get a value from settings store, this is the prefered way to access::

            >>> from dynaconf import settings
            >>> settings.get('KEY')

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :param fresh: Should reload from loaders store before access?
        :param dotted_lookup: Should perform dotted-path lookup?
        :param parent: Is there a pre-loaded parent in a nested data?
        :return: The value if found, default or None
        """

        if "." in key and dotted_lookup:
            return self._dotted_get(
                dotted_key=key,
                default=default,
                cast=cast,
                fresh=fresh,
                parent=parent,
            )

        key = upperfy(key)
        if key in self._deleted:
            return default

        if (
            fresh
            or self._fresh
            or key in getattr(self, "FRESH_VARS_FOR_DYNACONF", ())
        ) and key not in dir(default_settings):
            self.unset(key)
            self.execute_loaders(key=key)

        data = (parent or self.store).get(key, default)
        if cast:
            data = get_converter(cast, data, box_settings=self)
        return data

    def exists(self, key, fresh=False):
        """Check if key exists

        :param key: the name of setting variable
        :param fresh: if key should be taken from source direclty
        :return: Boolean
        """
        key = upperfy(key)
        if key in self._deleted:
            return False
        return self.get(key, fresh=fresh, default=missing) is not missing

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
        key = upperfy(key)
        data = self.environ.get(key, default)
        if data:
            if cast in converters:
                data = get_converter(cast, data, box_settings=self)
            if cast is True:
                data = parse_conf_data(data, tomlfy=True, box_settings=self)
        return data

    def exists_in_environ(self, key):
        """Return True if env variable is exported"""
        return upperfy(key) in self.environ

    def as_bool(self, key):
        """Partial method for get with bool cast"""
        return self.get(key, cast="@bool")

    def as_int(self, key):
        """Partial method for get with int cast"""
        return self.get(key, cast="@int")

    def as_float(self, key):
        """Partial method for get with float cast"""
        return self.get(key, cast="@float")

    def as_json(self, key):
        """Partial method for get with json cast"""
        return self.get(key, cast="@json")

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

    def from_env(self, env="", keep=False, **kwargs):
        """Return a new isolated settings object pointing to specified env.

        Example of settings.toml::

            [development]
            message = 'This is in dev'
            [other]
            message = 'this is in other env'

        Program::

            >>> from dynaconf import settings
            >>> print(settings.MESSAGE)
            'This is in dev'
            >>> print(settings.from_env('other').MESSAGE)
            'This is in other env'
            # The existing settings object remains the same.
            >>> print(settings.MESSAGE)
            'This is in dev'

        Arguments:
            env {str} -- Env to load (development, production, custom)

        Keyword Arguments:
            keep {bool} -- Keep pre-existing values (default: {False})
            kwargs {dict} -- Passed directly to new instance.
        """
        cache_key = f"{env}_{keep}_{kwargs}"
        if cache_key in self._env_cache:
            return self._env_cache[cache_key]

        new_data = {
            key: self.get(key)
            for key in dir(default_settings)
            if key.isupper() and key not in RENAMED_VARS
        }

        # This is here for backwards compatibility
        # To be removed on 4.x.x
        default_settings_paths = self.get("default_settings_paths")
        if default_settings_paths:  # pragma: no cover
            new_data["default_settings_paths"] = default_settings_paths

        if keep:
            # keep existing values from current env
            new_data.update(
                {
                    key: value
                    for key, value in self.store.to_dict().copy().items()
                    if key.isupper() and key not in RENAMED_VARS
                }
            )

        new_data.update(kwargs)
        new_data["FORCE_ENV_FOR_DYNACONF"] = env
        new_settings = LazySettings(**new_data)
        self._env_cache[cache_key] = new_settings
        return new_settings

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
            yield
        finally:
            if env.lower() != self.ENV_FOR_DYNACONF.lower():
                del self.loaded_envs[-1]
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

        if self.ENVIRONMENTS_FOR_DYNACONF is False:
            return "main"

        if self.FORCE_ENV_FOR_DYNACONF is not None:
            return self.FORCE_ENV_FOR_DYNACONF

        try:
            return self.loaded_envs[-1]
        except IndexError:
            return self.ENV_FOR_DYNACONF

    # compat
    current_namespace = current_env

    @property
    def settings_module(self):
        """Gets SETTINGS_MODULE variable"""
        settings_module = parse_conf_data(
            os.environ.get(
                self.ENVVAR_FOR_DYNACONF, self.SETTINGS_FILE_FOR_DYNACONF
            ),
            tomlfy=True,
            box_settings=self,
        )
        if settings_module != getattr(self, "SETTINGS_MODULE", None):
            self.set("SETTINGS_MODULE", settings_module)

        # This is for backewards compatibility, to be removed on 4.x.x
        if not self.SETTINGS_MODULE and self.get("default_settings_paths"):
            self.SETTINGS_MODULE = self.get("default_settings_paths")

        return self.SETTINGS_MODULE

    # Backwards compatibility see #169
    settings_file = settings_module

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

        if not isinstance(env, str):
            raise AttributeError("env should be a string")

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

    def unset(self, key, force=False):
        """Unset on all references

        :param key: The key to be unset
        :param force: Bypass default checks and force unset
        """
        key = upperfy(key.strip())
        if (
            key not in dir(default_settings)
            and key not in self._defaults
            or force
        ):
            delattr(self, key)
            self.store.pop(key, None)

    def unset_all(self, keys, force=False):  # pragma: no cover
        """Unset based on a list of keys

        :param keys: a list of keys
        :param force: Bypass default checks and force unset
        """
        for key in keys:
            self.unset(key, force=force)

    def _dotted_set(self, dotted_key, value, tomlfy=False, **kwargs):
        """Sets dotted keys as nested dictionaries.

        Dotted set will always reassign the value, to merge use `@merge` token

        Arguments:
            dotted_key {str} -- A traversal name e.g: foo.bar.zaz
            value {Any} -- The value to set to the nested value.

        Keyword Arguments:
            tomlfy {bool} -- Perform toml parsing (default: {False})
        """

        split_keys = dotted_key.split(".")
        existing_data = self.get(split_keys[0], {})
        new_data = DynaBox(box_settings=self)

        tree = new_data
        for k in split_keys[:-1]:
            tree = tree.setdefault(k, {})

        value = parse_conf_data(value, tomlfy=tomlfy, box_settings=self)
        tree[split_keys[-1]] = value

        if existing_data:
            object_merge(
                old={split_keys[0]: existing_data},
                new=new_data,
                tail=split_keys[-1],
            )

        self.update(data=new_data, tomlfy=tomlfy, **kwargs)

    def set(
        self,
        key,
        value,
        loader_identifier=None,
        tomlfy=False,
        dotted_lookup=True,
        is_secret=False,
        merge=False,
    ):
        """Set a value storing references for the loader

        :param key: The key to store
        :param value: The value to store
        :param loader_identifier: Optional loader name e.g: toml, yaml etc.
        :param tomlfy: Bool define if value is parsed by toml (defaults False)
        :param is_secret: Bool define if secret values is hidden on logs.
        :param merge: Bool define if existing nested data will be merged.
        """
        nested_sep = self.get("NESTED_SEPARATOR_FOR_DYNACONF")
        if nested_sep and nested_sep in key:
            # turn FOO__bar__ZAZ in `FOO.bar.ZAZ`
            key = key.replace(nested_sep, ".")

        if "." in key and dotted_lookup is True:
            return self._dotted_set(
                key, value, loader_identifier=loader_identifier, tomlfy=tomlfy
            )

        value = parse_conf_data(value, tomlfy=tomlfy, box_settings=self)
        key = upperfy(key.strip())
        existing = getattr(self, key, None)

        if getattr(value, "_dynaconf_del", None):
            # just in case someone use a `@del` in a first level var.
            self.unset(key, force=True)
            return

        if getattr(value, "_dynaconf_reset", False):  # pragma: no cover
            # just in case someone use a `@reset` in a first level var.
            # NOTE: @reset/Reset is deprecated in v3.0.0
            value = value.unwrap()

        if getattr(value, "_dynaconf_merge", False):
            # just in case someone use a `@merge` in a first level var
            if existing:
                object_merge(existing, value.unwrap())
            value = value.unwrap()

        if existing is not None and existing != value:
            # `dynaconf_merge` used in file root `merge=True`
            if merge:
                object_merge(existing, value)
            else:
                # `dynaconf_merge` may be used within the key structure
                value = self._merge_before_set(key, existing, value, is_secret)

        if isinstance(value, dict):
            value = DynaBox(value, box_settings=self)

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

    def update(
        self,
        data=None,
        loader_identifier=None,
        tomlfy=False,
        is_secret=False,
        merge=False,
        **kwargs,
    ):
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
        :param merge: Bool define if existing nested data will be merged.
        :param kwargs: extra values to update
        :return: None
        """
        data = data or {}
        data.update(kwargs)
        for key, value in data.items():
            self.set(
                key,
                value,
                loader_identifier=loader_identifier,
                tomlfy=tomlfy,
                is_secret=is_secret,
                merge=merge,
            )

    def _merge_before_set(self, key, existing, value, is_secret):
        """Merge the new value being set with the existing value before set"""

        global_merge = getattr(self, "MERGE_ENABLED_FOR_DYNACONF", False)

        if isinstance(value, dict):
            local_merge = value.pop(
                "dynaconf_merge", value.pop("dynaconf_merge_unique", None)
            )
            if local_merge not in (True, False, None) and not value:
                # In case `dynaconf_merge:` holds value not boolean - ref #241
                value = local_merge

            if global_merge or local_merge:
                safe_value = {k: "***" for k in value} if is_secret else value
                object_merge(existing, value)
                safe_value = (
                    {
                        k: ("***" if k in safe_value else v)
                        for k, v in value.items()
                    }
                    if is_secret
                    else value
                )

        if isinstance(value, (list, tuple)):
            local_merge = (
                "dynaconf_merge" in value or "dynaconf_merge_unique" in value
            )
            if global_merge or local_merge:
                value = list(value)
                unique = False

                if local_merge:
                    try:
                        value.remove("dynaconf_merge")
                    except ValueError:  # EAFP
                        value.remove("dynaconf_merge_unique")
                        unique = True

                original = set(value)
                object_merge(existing, value, unique=unique)
                safe_value = (
                    ["***" if item in original else item for item in value]
                    if is_secret
                    else value
                )
        return value

    @property
    def loaders(self):  # pragma: no cover
        """Return available loaders"""
        if self.LOADERS_FOR_DYNACONF in (None, 0, "0", "false", False):
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
        :param filename: optional custom filename to load
        """
        if key is None:
            default_loader(self, self._defaults)
        env = (env or self.current_env).upper()
        silent = silent or self.SILENT_ERRORS_FOR_DYNACONF
        self.pre_load(env, silent=silent, key=key)
        settings_loader(
            self, env=env, silent=silent, key=key, filename=filename
        )
        self.load_extra_yaml(env, silent, key)  # DEPRECATED
        enable_external_loaders(self)
        for loader in self.loaders:
            loader.load(self, env, silent=silent, key=key)
        self.load_includes(env, silent=silent, key=key)

    def pre_load(self, env, silent, key):
        """Do we have any file to pre-load before main settings file?"""
        preloads = self.get("PRELOAD_FOR_DYNACONF", [])
        if preloads:
            self.load_file(path=preloads, env=env, silent=silent, key=key)

    def load_includes(self, env, silent, key):
        """Do we have any nested includes we need to process?"""
        includes = self.get("DYNACONF_INCLUDE", [])
        includes.extend(ensure_a_list(self.get("INCLUDES_FOR_DYNACONF")))
        if includes:
            self.load_file(path=includes, env=env, silent=silent, key=key)
            # ensure env vars are the last thing loaded after all includes
            last_loader = self.loaders and self.loaders[-1]
            if last_loader and last_loader == env_loader:
                last_loader.load(self, env, silent, key)

    def load_file(self, path=None, env=None, silent=True, key=None):
        """Programmatically load files from ``path``.

        :param path: A single filename or a file list
        :param env: Which env to load from file (default current_env)
        :param silent: Should raise errors?
        :param key: Load a single key?
        """
        env = (env or self.current_env).upper()
        files = ensure_a_list(path)
        if files:
            already_loaded = set()
            for _filename in files:

                if py_loader.try_to_load_from_py_module_name(
                    obj=self, name=_filename, silent=True
                ):
                    # if it was possible to load from module name
                    # continue the loop.
                    continue

                filepath = os.path.join(
                    self._root_path or os.getcwd(), _filename
                )
                paths = [
                    p
                    for p in sorted(glob.glob(filepath))
                    if ".local." not in p
                ]
                local_paths = [
                    p for p in sorted(glob.glob(filepath)) if ".local." in p
                ]
                # Handle possible *.globs sorted alphanumeric
                for path in paths + local_paths:
                    if path in already_loaded:  # pragma: no cover
                        continue
                    settings_loader(
                        obj=self,
                        env=env,
                        silent=silent,
                        key=key,
                        filename=path,
                    )
                    already_loaded.add(path)

    @property
    def _root_path(self):
        """ROOT_PATH_FOR_DYNACONF or the path of first loaded file or '.'"""
        if self.ROOT_PATH_FOR_DYNACONF is not None:
            return self.ROOT_PATH_FOR_DYNACONF
        elif self._loaded_files:  # called once
            root_path = os.path.dirname(self._loaded_files[0])
            self.set("ROOT_PATH_FOR_DYNACONF", root_path)
            return root_path

    def load_extra_yaml(self, env, silent, key):
        """This is deprecated, kept for compat

        .. deprecated:: 1.0.0
            Use multiple settings or INCLUDES_FOR_DYNACONF files instead.
        """
        if self.get("YAML") is not None:
            warnings.warn(
                "The use of YAML var is deprecated, please define multiple "
                "filepaths instead: "
                "e.g: SETTINGS_FILE_FOR_DYNACONF = "
                "'settings.py,settings.yaml,settings.toml' or "
                "INCLUDES_FOR_DYNACONF=['path.toml', 'folder/*']"
            )
            yaml_loader.load(
                self,
                env=env,
                filename=self.find_file(self.get("YAML")),
                silent=silent,
                key=key,
            )

    def path_for(self, *args):
        """Path containing _root_path"""
        if args and args[0].startswith(os.path.sep):
            return os.path.join(*args)
        return os.path.join(self._root_path or os.getcwd(), *args)

    def find_file(self, *args, **kwargs):
        kwargs.setdefault("project_root", self._root_path)
        kwargs.setdefault(
            "skip_files", self.get("SKIP_FILES_FOR_DYNACONF", [])
        )
        return find_file(*args, **kwargs)

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
        env = env or self.ENVVAR_PREFIX_FOR_DYNACONF or "DYNACONF"
        with self.using_env(env):
            value = self.get_fresh(key)
            return value is True or value in true_values

    def populate_obj(self, obj, keys=None, ignore=None):
        """Given the `obj` populate it using self.store items.

        :param obj: An object to be populated, a class instance.
        :param keys: A list of keys to be included.
        :param ignore: A list of keys to be excluded.
        """
        keys = keys or self.keys()
        for key in keys:
            key = upperfy(key)
            if ignore and key in ignore:
                continue
            value = self.get(key, empty)
            if value is not empty:
                setattr(obj, key, value)

    def dynaconf(self):  # pragma: no cover
        """A proxy to access internal methods and attributes

        Starting in 3.0.0 Dynaconf now allows first level lower case
        keys that are not reserved keyword, so this is a proxy to
        internal methods and attrs.
        """
        return  # TOBE IMPLEMENTED

    @property
    def logger(self):  # pragma: no cover
        """backwards compatibility with pre 3.0 loaders
        In dynaconf 3.0.0 logger and debug messages has been removed.
        """
        warnings.warn(
            "logger and DEBUG messages has been removed on dynaconf 3.0.0"
        )
        import logging  # noqa

        return logging.getLogger("dynaconf")

    def is_overridden(self, setting):
        """This is to provide Django DJDT support: issue 382"""
        return False


"""Attributes created on Settings before 3.0.0"""
RESERVED_ATTRS = (
    [
        item[0]
        for item in inspect.getmembers(LazySettings)
        if not item[0].startswith("__")
    ]
    + [
        item[0]
        for item in inspect.getmembers(Settings)
        if not item[0].startswith("__")
    ]
    + [
        "_defaults",
        "_deleted",
        "_env_cache",
        "_fresh",
        "_kwargs",
        "_loaded_by_loaders",
        "_loaded_envs",
        "_loaded_files",
        "_loaders",
        "_memoized",
        "_not_installed_warnings",
        "_store",
        "_warn_dynaconf_global_settings",
        "environ",
        "SETTINGS_MODULE",
        "validators",
    ]
)
