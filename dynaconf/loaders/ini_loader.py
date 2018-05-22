# coding: utf-8
from dynaconf.constants import INI_EXTENSIONS
try:
    from configobj import ConfigObj
except ImportError as e:  # pragma: no cover
    ConfigObj = None

from dynaconf.utils.files import find_file

IDENTIFIER = 'ini_loader'


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "settings" a single key or all keys from ini file
    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :return: None
    """
    if ConfigObj is None:  # pragma: no cover
        obj.logger.warning(
            "configobj package is not installed in your environment.\n"
            "To use this loader you have to install it with\n"
            "pip install configobj\n"
            "or\n"
            "pip install dynaconf[ini]"
        )
        return

    filename = filename or obj.get('INI')
    if not filename:
        return

    env = env or obj.current_env

    # can be a filename settings.yml
    # can be a multiple fileset settings1.ini, settings2.ini etc
    # and also a list of strings ['aaa:a', 'bbb:c']
    # and can also be a single string 'aa:a'
    if not isinstance(filename, (list, tuple)):
        split_files = filename.split(',')
        if all([f.endswith(INI_EXTENSIONS) for f in split_files]):  # noqa
            files = split_files  # it is a ['file.ini', ...]
        else:  # it is a single ini string
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
    load_from_ini(obj, files, env_list, silent, key)


def load_from_ini(obj, files, envs, silent=True, key=None):
    for ini_file in files:
        if ini_file.endswith(INI_EXTENSIONS):  # pragma: no cover
            obj.logger.debug('Trying to load ini {}'.format(ini_file))
            try:
                ini_data = ConfigObj(
                    open(find_file(ini_file, usecwd=True))
                ).dict()
            except IOError as e:
                obj.logger.debug(
                    "Unable to load ini file {}".format(str(e)))
                ini_data = None
        else:
            # for tests it is possible to pass ini string
            ini_data = ConfigObj(ini_file.split('\n')).dict()

        if not ini_data:
            continue

        ini_data = {k.lower(): value for k, value in ini_data.items()}

        for env in envs:

            data = {}
            try:
                data = ini_data[env.lower()]
            except KeyError:
                message = '%s env not defined in %s' % (
                    env, ini_file)
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
