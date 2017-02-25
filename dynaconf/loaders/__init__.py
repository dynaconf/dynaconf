import os
import importlib
from dynaconf import default_settings
from dynaconf.loaders import yaml_loader


def default_loader(obj):
    for key, value in default_settings.__dict__.items():
        if key.isupper():
            obj.set(key, value, loader_identifier='DEFAULT')


def module_loader(obj, settings_module=None, namespace=None):
    """Loads from defined settings module, path or yaml"""
    settings_module = settings_module or obj.settings_module
    if not settings_module:  # pragma: no cover
        return

    if settings_module.endswith(('.yaml', '.yml')):
        yaml_loader.load(obj, filename=settings_module, namespace=namespace)
        return

    # load from default defined module if exists (never gets cleaned)
    load_from_module(obj, settings_module)

    if namespace and namespace != obj.DYNACONF_NAMESPACE:
        if settings_module.endswith('.py'):
            dirname = os.path.dirname(settings_module)
            filename, extension = os.path.splitext(
                os.path.basename(settings_module)
            )
            new_filename = "{0}_{1}{2}".format(
                namespace.lower(), filename, extension
            )
            namespace_settings_module = os.path.join(
                dirname, new_filename
            )
        else:
            namespace_settings_module = "{0}_{1}".format(
                namespace.lower(), settings_module
            )

        load_from_module(
            obj,
            namespace_settings_module,
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
