import os
import errno
import types
import importlib
from dynaconf import default_settings
from dynaconf.utils.files import find_file
from dynaconf.utils import dictmerge, DynaconfDict, raw_logger


def load(obj, settings_module, identifier='py', silent=False, key=None):
    obj.logger.debug('executing load_from_module: %s', settings_module)
    try:
        mod = importlib.import_module(settings_module)
        loaded_from = 'module'
    except (ImportError, TypeError):
        mod = import_from_filename(settings_module, silent=silent)
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


def import_from_filename(filename, silent=False):  # pragma: no cover
    """If settings_module is a path use this."""
    if not filename.endswith('.py'):
        filename = '{0}.py'.format(filename)

    if filename in default_settings.SETTINGS_MODULE_FOR_DYNACONF:
        silent = True
    mod = types.ModuleType('config')
    mod.__file__ = filename
    mod._is_error = False
    try:
        with open(find_file(filename)) as config_file:
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
        raw_logger().debug(e.strerror)
        mod._is_error = True
    return mod


def write(settings_path, settings_data, merge=True):
    if settings_path.exists() and merge:  # pragma: no cover
        existing = DynaconfDict()
        load(existing, str(settings_path))
        settings_data = dictmerge(
            existing,
            settings_data
        )
    with open(settings_path, 'w') as f:
        f.writelines(
            ["{} = {}\n".format(k.upper(), repr(v))
             for k, v in settings_data.items()]
        )
