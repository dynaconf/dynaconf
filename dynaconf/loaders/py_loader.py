import os
import errno
import types
import importlib
from dynaconf import default_settings
from dynaconf.utils.files import find_file
from dynaconf.utils import dictmerge, DynaconfDict, raw_logger


def load(obj, settings_module, identifier='py', silent=False, key=None):
    """Tries to import a python module"""
    try:
        mod = importlib.import_module(settings_module)
        loaded_from = 'module'
    except (ImportError, TypeError):
        mod = import_from_filename(settings_module, silent=silent)
        if mod and mod._is_error:
            loaded_from = None
        else:
            loaded_from = 'filename'

    if mod and loaded_from:
        obj.logger.debug(
            "py_loader: {}".format(mod)
        )
    else:
        obj.logger.debug('py_loader: %s (Ignoring, Not Found)',
                         settings_module)
        return

    for setting in dir(mod):
        if setting.isupper():
            if key is None or key == setting:
                setting_value = getattr(mod, setting)
                obj.logger.debug(
                    'py_loader: loading %s: %s (%s)',
                    setting,
                    '*****' if 'secret' in settings_module else setting_value,
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
    """If settings_module is a filename path import it."""
    if not filename.endswith('.py'):
        filename = '{0}.py'.format(filename)

    if filename in default_settings.SETTINGS_MODULE_FOR_DYNACONF:
        silent = True
    mod = types.ModuleType(filename.rstrip('.py'))
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
            'py_loader: error loading file (%s %s)\n'
        ) % (e.strerror, filename)
        if silent and e.errno in (errno.ENOENT, errno.EISDIR):
            return
        raw_logger().debug(e.strerror)
        mod._is_error = True
    return mod


def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    if settings_path.exists() and merge:  # pragma: no cover
        existing = DynaconfDict()
        load(existing, str(settings_path))
        settings_data = dictmerge(
            existing,
            settings_data
        )
    with open(str(settings_path), 'w') as f:
        f.writelines(
            ["{} = {}\n".format(k.upper(), repr(v))
             for k, v in settings_data.items()]
        )
