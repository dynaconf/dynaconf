# coding: utf-8
# In order to have multiple envs support use BaseLoader
# Take a look in dynaconf/loaders/json_loader.py


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
    # This loader reads the .sff file // Stupid File Format
    keys = []
    values = []
    for line in open('settings.sff').readlines():
        if line.startswith('#'):
            continue
        if line.startswith('KEYS:'):
            keys = line.strip('KEYS:').strip('\n').split(';')
        if line.startswith('VALUES:'):
            values = line.strip('VALUES:').strip('\n').split(';')
    # // PLEASE DON'T USE THIS SFF file format :)

    data = dict(zip(keys, values))
    obj.logger.debug('Sff loader: loading: {0}'.format(data))
    obj.update(data)
