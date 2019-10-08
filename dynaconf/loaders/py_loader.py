import errno
import importlib
import inspect
import io
import types
from contextlib import suppress
from pathlib import Path

from dynaconf import default_settings
from dynaconf.utils import DynaconfDict
from dynaconf.utils import object_merge
from dynaconf.utils import raw_logger
from dynaconf.utils import upperfy
from dynaconf.utils.files import find_file


def load(obj, settings_module, identifier="py", silent=False, key=None):
    """Tries to import a python module"""
    mod, loaded_from = get_module(obj, settings_module, silent)

    if mod and loaded_from:
        obj.logger.debug("py_loader: {}".format(mod))
    else:
        obj.logger.debug(
            "py_loader: %s (Ignoring, Not Found)", settings_module
        )
        return

    load_from_python_object(obj, mod, settings_module, key, identifier)


def load_from_python_object(
    obj, mod, settings_module, key=None, identifier=None
):
    file_merge = getattr(mod, "dynaconf_merge", False) or getattr(
        mod, "DYNACONF_MERGE", False
    )
    for setting in dir(mod):
        # at least 3 first chars should be upper to be considered a setting var
        if setting[:3].isupper():
            if key is None or key == setting:
                setting_value = getattr(mod, setting)
                obj.logger.debug(
                    "py_loader: loading %s: %s (%s)",
                    setting,
                    "*****" if "secret" in settings_module else setting_value,
                    identifier,
                )
                obj.set(
                    setting,
                    setting_value,
                    loader_identifier=identifier,
                    merge=file_merge,
                )
    obj._loaded_files.append(mod.__file__)


def try_to_load_from_py_module_name(
    obj, name, key=None, identifier="py", silent=False
):
    """Try to load module by its string name.

    Arguments:
        obj {LAzySettings} -- Dynaconf settings instance
        name {str} -- Name of the module e.g: foo.bar.zaz

    Keyword Arguments:
        key {str} -- Single key to be loaded (default: {None})
        identifier {str} -- Name of identifier to store (default: 'py')
        silent {bool} -- Weather to raise or silence exceptions.
    """
    ctx = suppress(ImportError, TypeError) if silent else suppress()

    with ctx:
        mod = importlib.import_module(name)
        load_from_python_object(obj, mod, name, key, identifier)
        return True  # loaded ok!
    # if it reaches this point that means exception occurred, module not found.
    return False


def get_module(obj, filename, silent=False):
    logger = raw_logger()
    try:
        logger.debug("Trying to import %s", filename)
        mod = importlib.import_module(filename)
        loaded_from = "module"
    except (ImportError, TypeError):
        logger.debug("Cant import %s trying to load from file", filename)
        mod = import_from_filename(obj, filename, silent=silent)
        if mod and not mod._is_error:
            loaded_from = "filename"
        else:
            # it is important to return None in case of not loaded
            loaded_from = None
    return mod, loaded_from


def import_from_filename(obj, filename, silent=False):  # pragma: no cover
    """If settings_module is a filename path import it."""
    if filename in [item.filename for item in inspect.stack()]:
        raise ImportError(
            "Looks like you are loading dynaconf "
            "from inside the {} file and then it is trying "
            "to load itself entering in a circular reference "
            "problem. To solve it you have to "
            "invoke your program from another root folder "
            "or rename your program file.".format(filename)
        )

    _find_file = getattr(obj, "find_file", find_file)
    if not filename.endswith(".py"):
        filename = "{0}.py".format(filename)

    if filename in default_settings.SETTINGS_FILE_FOR_DYNACONF:
        silent = True
    mod = types.ModuleType(filename.rstrip(".py"))
    mod.__file__ = filename
    mod._is_error = False
    try:
        with io.open(
            _find_file(filename),
            encoding=default_settings.ENCODING_FOR_DYNACONF,
        ) as config_file:
            exec(compile(config_file.read(), filename, "exec"), mod.__dict__)
    except IOError as e:
        e.strerror = ("py_loader: error loading file (%s %s)\n") % (
            e.strerror,
            filename,
        )
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
        object_merge(existing, settings_data)
    with io.open(
        str(settings_path),
        "w",
        encoding=default_settings.ENCODING_FOR_DYNACONF,
    ) as f:
        f.writelines(
            [
                "{} = {}\n".format(upperfy(k), repr(v))
                for k, v in settings_data.items()
            ]
        )
