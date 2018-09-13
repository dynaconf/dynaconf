# coding: utf-8
import io
from dynaconf import default_settings
from dynaconf.loaders.base import BaseLoader
from dynaconf.constants import JSON_EXTENSIONS
from dynaconf.utils import dictmerge
import json


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
    loader = BaseLoader(
        obj=obj,
        env=env,
        identifier='json',
        extensions=JSON_EXTENSIONS,
        file_reader=json.load,
        string_reader=json.loads
    )
    loader.load(filename=filename, key=key, silent=silent)


def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """

    if settings_path.exists() and merge:  # pragma: no cover
        settings_data = dictmerge(
            json.load(
                io.open(
                    str(settings_path),
                    encoding=default_settings.ENCODING_FOR_DYNACONF
                )
            ),
            settings_data
        )

    json.dump(
        settings_data,
        io.open(
            str(settings_path), 'w',
            encoding=default_settings.ENCODING_FOR_DYNACONF
        )
    )
