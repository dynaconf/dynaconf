import io
import errno
import types
import importlib
import inspect
from pathlib import Path
from dynaconf import default_settings
from dynaconf.utils.files import find_file
from dynaconf.utils import DynaconfDict, object_merge, raw_logger


def load(obj, settings_module, identifier='py', silent=False, key=None):
    """Tries to import a python module"""
    mod, loaded_from = get_module(obj, settings_module, silent)

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

    obj._loaded_files.append(mod.__file__)


def get_module(obj, filename, silent=False):
    logger = raw_logger()
    try:
        logger.debug('Trying to import %s', filename)
        mod = importlib.import_module(filename)
        loaded_from = 'module'
    except (ImportError, TypeError):
        logger.debug('Cant import %s trying to load from file', filename)
        mod = import_from_filename(obj, filename, silent=silent)
        if mod and not mod._is_error:
            loaded_from = 'filename'
        else:
            loaded_from = None
    return mod, loaded_from


def import_from_filename(obj, filename, silent=False):  # pragma: no cover
    """If settings_module is a filename path import it."""
    if filename in [item.filename for item in inspect.stack()]:
        raise ImportError(
            'Looks like you are loading dynaconf '
            'from inside the {} file and then it is trying '
            'to load itself entering in a circular reference '
            'problem. To solve it you have to '
            'invoke your program from another root folder '
            'or rename your program file.'
            .format(filename)
        )

    _find_file = getattr(obj, 'find_file', find_file)
    if not filename.endswith('.py'):
        filename = '{0}.py'.format(filename)

    if filename in default_settings.SETTINGS_MODULE_FOR_DYNACONF:
        silent = True
    mod = types.ModuleType(filename.rstrip('.py'))
    mod.__file__ = filename
    mod._is_error = False
    try:
        with io.open(
            _find_file(filename),
            encoding=default_settings.ENCODING_FOR_DYNACONF
        ) as config_file:
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
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        existing = DynaconfDict()
        load(existing, str(settings_path))
        object_merge(
            existing,
            settings_data
        )
    with io.open(
        str(settings_path), 'w',
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ) as f:
        f.writelines(
            ["{} = {}\n".format(k.upper(), repr(v))
             for k, v in settings_data.items()]
        )
