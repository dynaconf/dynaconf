# coding: utf-8
from dynaconf.constants import JSON_EXTENSIONS
import json
from dynaconf.utils.files import find_file

IDENTIFIER = 'json_loader'


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "settings" a single key or all keys from json file
    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :return: None
    """
    filename = filename or obj.get('JSON')
    if not filename:
        return

    env = env or obj.current_env

    # can be a filename settings.yml
    # can be a multiple fileset settings1.json, settings2.json etc
    # and also a list of strings ['aaa:a', 'bbb:c']
    # and can also be a single string 'aa:a'
    if not isinstance(filename, (list, tuple)):
        split_files = filename.split(',')
        if all([f.endswith(JSON_EXTENSIONS) for f in split_files]):  # noqa
            files = split_files  # it is a ['file.json', ...]
        else:  # it is a single json string
            files = [filename]
    else:  # it is already a list/tuple
        files = filename

    # add the default env
    env_list = [obj.get('DEFAULT_ENV_FOR_DYNACONF')]
    # add the current env
    if env and env not in env_list:
        env_list.append(env)
    # add the global env
    global_env = obj.get('GLOBAL_ENV_FOR_DYNACONF')
    if global_env not in env_list:
        env_list.append(global_env)
    env_list.append('GLOBAL')
    # load all envs
    load_from_json(obj, files, env_list, silent, key)


def load_from_json(obj, files, envs, silent=True, key=None):

    for json_file in files:
        if json_file.endswith(JSON_EXTENSIONS):  # pragma: no cover
            obj.logger.debug('Trying to load json {}'.format(json_file))
            try:
                json_data = json.load(
                    open(find_file(json_file, usecwd=True))
                )
            except (IOError, json.decoder.JSONDecodeError) as e:
                obj.logger.debug(
                    "Unable to load json {} file {}".format(json_file, str(e)))
                json_data = None
        else:
            # for tests it is possible to pass json string
            json_data = json.loads(json_file)

        if not json_data:
            continue

        json_data = {key.lower(): value for key, value in json_data.items()}

        for env in envs:

            data = {}
            try:
                data = json_data[env.lower()]
            except KeyError:
                message = '%s env not defined in %s' % (
                    env, json_file)
                if silent:
                    obj.logger.warning(message)
                else:
                    raise KeyError(message)

            if env != obj.get('DEFAULT_ENV_FOR_DYNACONF'):
                identifier = "{0}_{1}".format(IDENTIFIER, env.lower())
            else:
                identifier = IDENTIFIER

            if not key:
                obj.update(data, loader_identifier=identifier)
            elif key in data:
                obj.set(key, data.get(key), loader_identifier=identifier)


def clean(obj, env, silent=True):  # noqa
    for identifier, data in obj.loaded_by_loaders.items():
        if identifier.startswith('json_loader'):
            for key in data:
                obj.logger.debug("cleaning: %s (%s)", key, identifier)
                obj.unset(key)
