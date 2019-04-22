import io
from pathlib import Path

from dynaconf import default_settings
from dynaconf.constants import TOML_EXTENSIONS
from dynaconf.loaders.base import BaseLoader
from dynaconf.utils import object_merge

try:
    import toml
except ImportError:  # pragma: no cover
    toml = None


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "obj" a single key or all keys from source file.

    :param obj: the settings instance
    :param env: settings current env default='development'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :param filename: Optional custom filename to load
    :return: None
    """
    if toml is None:  # pragma: no cover
        BaseLoader.warn_not_installed(obj, "toml")
        return

    loader = BaseLoader(
        obj=obj,
        env=env,
        identifier="toml",
        extensions=TOML_EXTENSIONS,
        file_reader=toml.load,
        string_reader=toml.loads,
    )
    loader.load(filename=filename, key=key, silent=silent)


def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        with io.open(
            str(settings_path), encoding=default_settings.ENCODING_FOR_DYNACONF
        ) as open_file:
            object_merge(toml.load(open_file), settings_data)

    with io.open(
        str(settings_path),
        "w",
        encoding=default_settings.ENCODING_FOR_DYNACONF,
    ) as open_file:
        toml.dump(settings_data, open_file)
