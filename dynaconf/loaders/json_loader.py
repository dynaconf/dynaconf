# coding: utf-8
from dynaconf.loaders.base import BaseLoader
from dynaconf.constants import JSON_EXTENSIONS
from dynaconf.utils import dictmerge
import json


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "obj" a single key or all keys from source file
    :param obj: the settings instance
    :param env: settings current env default='development'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :param filename: Custom filename to load
    :return: None
    """
    loader = BaseLoader(
        obj=obj,
        env=env,
        identifier='json',
        module_is_loaded=json,
        extensions=JSON_EXTENSIONS,
        file_reader=json.load,
        string_reader=json.loads
    )
    loader.load(filename=filename, key=key, silent=silent)


def write(settings_path, settings_data, merge=True):
    if settings_path.exists() and merge:  # pragma: no cover
        settings_data = dictmerge(
            json.load(open(settings_path)),
            settings_data
        )
    json.dump(settings_data, open(settings_path, 'w'))
