# coding: utf-8
from dynaconf.loaders.base import BaseLoader
from dynaconf.constants import INI_EXTENSIONS
from dynaconf.utils import dictmerge
try:
    from configobj import ConfigObj
except ImportError as e:  # pragma: no cover
    ConfigObj = None


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
        identifier='ini',
        module_is_loaded=ConfigObj,
        extensions=INI_EXTENSIONS,
        file_reader=lambda fileobj: ConfigObj(fileobj).dict(),
        string_reader=lambda strobj: ConfigObj(strobj.split('\n')).dict()
    )
    loader.load(filename=filename, key=key, silent=silent)


def write(settings_path, settings_data, merge=True):
    if settings_path.exists() and merge:  # pragma: no cover
        settings_data = dictmerge(
            ConfigObj(open(settings_path)).dict(),
            settings_data
        )
    new = ConfigObj()
    new.update(settings_data)
    new.write(open(settings_path, 'bw'))
