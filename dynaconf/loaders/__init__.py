import os
import importlib
from dynaconf import constants as ct
from dynaconf import default_settings
from dynaconf.loaders import (
    yaml_loader, toml_loader, json_loader, ini_loader
)
from dynaconf.utils.parse_conf import false_values


def default_loader(obj, defaults=None):
    defaults = defaults or {}
    default_settings_values = {
        key: value
        for key, value
        in default_settings.__dict__.items()
        if key.isupper()
    }

    all_keys = list(default_settings_values.keys()) + list(defaults.keys())

    for key in all_keys:
        value = defaults.get(key, default_settings_values.get(key))
        obj.logger.debug("default_loader:loading: %s:%s", key, value)
        obj.set(key, value)

    # start dotenv to get default env vars from there
    # check overrides in env vars
    default_settings.start_dotenv(obj)
    for key in all_keys:
        env_value = obj.get_env(key, '_not_found')
        if env_value != '_not_found':
            obj.logger.debug(
                "default_loader:overriding from envvar: %s:%s",
                key, env_value
            )
            obj.set(key, env_value)


def settings_loader(obj, settings_module=None, namespace=None,
                    silent=True, key=None):
    """Loads from defined settings module, path or yaml"""
    obj.logger.debug('executing settings_loader: %s', settings_module)
    settings_module = settings_module or obj.settings_module
    if not settings_module:  # pragma: no cover
        return

    if not isinstance(settings_module, (list, tuple)):
        files = settings_module.split(',')
    else:
        files = [settings_module]

    obj.logger.debug("files %s", files)

    for mod_file in files:
        # can be set to multiple files settings.py,settings.yaml,...

        # Cascade all loaders
        loaders = [
            {'ext': ct.YAML_EXTENSIONS, 'name': 'YAML', 'loader': yaml_loader},
            {'ext': ct.TOML_EXTENSIONS, 'name': 'TOML', 'loader': toml_loader},
            {'ext': ct.INI_EXTENSIONS, 'name': 'INI', 'loader': ini_loader},
            {'ext': ct.JSON_EXTENSIONS, 'name': 'JSON', 'loader': json_loader},
        ]

        for loader in loaders:
            if mod_file.endswith(loader['ext']):
                obj.logger.debug(
                    "Trying to load {0}:{1}".format(loader['name'], mod_file)
                )
                loader['loader'].load(
                    obj,
                    filename=mod_file,
                    namespace=namespace,
                    silent=silent,
                    key=key
                )
                continue

        if mod_file.endswith(ct.ALL_EXTENSIONS):
            continue

        # must be Python file or module

        obj.logger.debug("Trying to load Python module {}".format(mod_file))

        # load from default defined module if exists (never gets cleaned)
        load_from_module(obj, mod_file, key=key)

        if namespace and namespace != obj.BASE_NAMESPACE_FOR_DYNACONF:
            if mod_file.endswith('.py'):
                dirname = os.path.dirname(mod_file)
                filename, extension = os.path.splitext(
                    os.path.basename(mod_file)
                )
                new_filename = "{0}_{1}{2}".format(
                    namespace.lower(), filename, extension
                )
                namespace_mod_file = os.path.join(
                    dirname, new_filename
                )
            else:
                namespace_mod_file = "{0}_{1}".format(
                    namespace.lower(), mod_file
                )

            load_from_module(
                obj,
                namespace_mod_file,
                identifier='PY_MODULE_{0}'.format(namespace.upper()),
                silent=True,
                key=key
            )


def enable_external_loaders(obj):
    """Enable external service loaders like VAULT_ and REDIS_"""
    for name, loader in ct.EXTERNAL_LOADERS.items():
        enabled = getattr(
            obj,
            '{}_FOR_DYNACONF_ENABLED'.format(name.upper()),
            False
        )
        if (
              enabled and
              enabled not in false_values and
              loader not in obj.LOADERS_FOR_DYNACONF
            ):  # noqa
            obj.LOADERS_FOR_DYNACONF.append(loader)


def load_from_module(obj, settings_module,
                     identifier='PY_MODULE', silent=False, key=None):
    obj.logger.debug('executing load_from_module: %s', settings_module)
    try:
        mod = importlib.import_module(settings_module)
        loaded_from = 'module'
    except (ImportError, TypeError):
        mod = obj.import_from_filename(settings_module, silent=silent)
        if mod and mod._is_error:
            loaded_from = None
        else:
            loaded_from = 'filename'
        obj.logger.debug(mod)

    if loaded_from:
        obj.logger.debug(
            "Module {} Loaded from {}".format(settings_module, loaded_from)
        )

    for setting in dir(mod):
        if setting.isupper():
            if key is None or key == setting:
                setting_value = getattr(mod, setting)
                obj.logger.debug(
                    'module_loader:loading %s: %s (%s)',
                    setting,
                    setting_value,
                    identifier
                )
                obj.set(setting, setting_value, loader_identifier=identifier)

    if not hasattr(obj, 'PROJECT_ROOT_FOR_DYNACONF'):
        root = os.path.realpath(
            os.path.dirname(os.path.abspath(settings_module))
        ) if loaded_from == 'module' else os.getcwd()
        obj.set('PROJECT_ROOT_FOR_DYNACONF',
                root, loader_identifier=identifier)


def settings_cleaner(obj, namespace, silent=True):  # noqa
    """The main python module never gets cleaned, only the _namespaced"""
    for identifier, data in obj.loaded_by_loaders.items():
        if identifier.startswith('PY_MODULE'):
            for key in data:
                obj.logger.debug("cleaning: %s (%s)", key, identifier)
                obj.unset(key)
