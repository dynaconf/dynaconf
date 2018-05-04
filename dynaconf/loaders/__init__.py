import os
import importlib
from dynaconf import constants as ct
from dynaconf import default_settings
from dynaconf.loaders import (
    yaml_loader, env_loader, toml_loader, json_loader, ini_loader
)


def default_loader(obj):
    for key, value in default_settings.__dict__.items():
        if key.isupper():
            obj.set(key, value, loader_identifier='DEFAULT')


def pre_env_loader(obj, namespace=None, silent=False, key=None):
    """Load default env values before any other env loader"""
    namespace = namespace or 'DYNACONF'
    env_loader.load_from_env('env_loader', key, namespace, obj, silent)


def module_loader(obj, settings_module=None, namespace=None, silent=False):
    """Loads from defined settings module, path or yaml"""
    settings_module = settings_module or obj.settings_module
    if not settings_module:  # pragma: no cover
        return

    if not isinstance(settings_module, (list, tuple)):
        files = settings_module.split(',')
    else:
        files = [settings_module]

    for mod_file in files:
        # can be set to multiple files settings.py,settings.yaml,...

        # NOTE: all this cascade can be refactored to use a loader class!
        if mod_file.endswith(ct.YAML_EXTENSIONS):
            obj.logger.info("Trying to load YAML {}".format(mod_file))
            yaml_loader.load(
                obj,
                filename=mod_file,
                namespace=namespace,
                silent=silent
            )
            continue

        if mod_file.endswith(ct.TOML_EXTENSIONS):
            obj.logger.info("Trying to load TOML {}".format(mod_file))
            toml_loader.load(
                obj,
                filename=mod_file,
                namespace=namespace,
                silent=silent
            )
            continue

        if mod_file.endswith(ct.INI_EXTENSIONS):
            obj.logger.info("Trying to load INI {}".format(mod_file))
            ini_loader.load(
                obj,
                filename=mod_file,
                namespace=namespace,
                silent=silent
            )
            continue

        if mod_file.endswith(ct.JSON_EXTENSIONS):
            obj.logger.info("Trying to load JSON {}".format(mod_file))
            json_loader.load(
                obj,
                filename=mod_file,
                namespace=namespace,
                silent=silent
            )
            continue

        obj.logger.info("Trying to load Python module {}".format(mod_file))

        # load from default defined module if exists (never gets cleaned)
        load_from_module(obj, mod_file)

        if namespace and namespace != obj.DYNACONF_NAMESPACE:
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
                identifier='DEFAULT_MODULE_{0}'.format(namespace.upper()),
                silent=True
            )


def load_from_module(obj, settings_module,
                     identifier='DEFAULT_MODULE', silent=False):
    try:
        mod = importlib.import_module(settings_module)
        loaded_from = 'module'
    except ImportError:
        mod = obj.import_from_filename(settings_module, silent=silent)
        loaded_from = 'filename'

    obj.logger.info(
        "Module {} Loaded from {}".format(settings_module, loaded_from))

    for setting in dir(mod):
        if setting.isupper():
            setting_value = getattr(mod, setting)
            obj.set(setting, setting_value, loader_identifier=identifier)

    if not hasattr(obj, 'PROJECT_ROOT'):
        root = os.path.realpath(
            os.path.dirname(os.path.abspath(settings_module))
        ) if loaded_from == 'module' else os.getcwd()
        obj.set('PROJECT_ROOT', root, loader_identifier=identifier)


def module_cleaner(obj, namespace, silent=True):  # noqa
    for identifier, data in obj.loaded_by_loaders.items():
        if identifier.startswith('DEFAULT_MODULE_'):
            for key in data:
                obj.unset(key)
