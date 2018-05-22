# coding: utf-8
from dynaconf.constants import TOML_EXTENSIONS
try:
    import toml
except ImportError as e:  # pragma: no cover
    toml = None

from dynaconf.utils.files import find_file

IDENTIFIER = 'toml_loader'


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "settings" a single key or all keys from toml file
    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :return: None
    """
    if toml is None:  # pragma: no cover
        obj.logger.warning(
            "toml package is not installed in your environment.\n"
            "To use this loader you have to install it with\n"
            "pip install toml\n"
            "or\n"
            "pip install dynaconf[toml]"
        )
        return

    filename = filename or obj.get('TOML')
    if not filename:
        return

    env = env or obj.current_env

    # can be a filename settings.yml
    # can be a multiple fileset settings1.toml, settings2.toml etc
    # and also a list of strings ['aaa:a', 'bbb:c']
    # and can also be a single string 'aa:a'
    if not isinstance(filename, (list, tuple)):
        split_files = filename.split(',')
        if all([f.endswith(TOML_EXTENSIONS) for f in split_files]):
            files = split_files  # it is a ['file.toml', ...]
        else:  # it is a single TOML string
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
    load_from_toml(obj, files, env_list, silent, key)


def load_from_toml(obj, files, envs, silent=True, key=None):

    for toml_file in files:
        if toml_file.endswith(TOML_EXTENSIONS):  # pragma: no cover
            obj.logger.debug('Trying to load TOML {}'.format(toml_file))
            try:
                toml_data = toml.load(
                    open(find_file(toml_file, usecwd=True))
                )
            except IOError as e:
                obj.logger.debug(
                    "Unable to load TOML file {}".format(str(e)))
                toml_data = None
        else:
            # for tests it is possible to pass TOML string
            toml_data = toml.loads(toml_file)

        if not toml_data:
            continue

        toml_data = {key.lower(): value for key, value in toml_data.items()}

        for env in envs:
            obj.logger.debug('Loading %s env', env)
            data = {}
            try:
                data = toml_data[env.lower()]
            except KeyError:
                message = '%s env not defined in %s' % (
                    env, toml_file)
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
