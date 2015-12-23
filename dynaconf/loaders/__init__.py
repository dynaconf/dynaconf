import os
import importlib
from dynaconf import default_settings


def default_loader(obj):
    for key, value in default_settings.__dict__.items():
        if key.isupper():
            obj.set(key, value)


def module_loader(obj, settings_module=None):
    settings_module = settings_module or obj.settings_module
    if not settings_module:
        return

    try:
        mod = importlib.import_module(settings_module)
        loaded_from = 'module'
    except ImportError:
        mod = obj.import_from_filename(settings_module)
        loaded_from = 'filename'

    for setting in dir(mod):
        if setting.isupper():
            setting_value = getattr(mod, setting)
            obj.set(setting, setting_value)

    if not hasattr(obj, 'PROJECT_ROOT'):
        root = os.path.realpath(
            os.path.dirname(os.path.abspath(settings_module))
        ) if loaded_from == 'module' else os.getcwd()
        obj.set('PROJECT_ROOT', root)
