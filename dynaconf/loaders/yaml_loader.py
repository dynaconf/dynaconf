# coding: utf-8
from dynaconf.constants import YAML_EXTENSIONS
try:
    import yaml
except ImportError as e:  # pragma: no cover
    yaml = None

from dynaconf.utils.files import find_file

IDENTIFIER = 'yaml_loader'


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "settings" a single key or all keys from yaml file
    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :return: None
    """
    if yaml is None:  # pragma: no cover
        obj.logger.warning(
            "PyYAML package is not installed in your environment.\n"
            "To use this loader you have to install it with\n"
            "pip install PyYAML\n"
            "or\n"
            "pip install dynaconf[yaml]"
        )
        return

    filename = filename or obj.get('YAML')
    if not filename:
        return

    env = env or obj.current_env

    # can be a filename settings.yml
    # can be a multiple fileset settings1.yml, settings2.yaml etc
    # and also a list of strings ['aaa:a', 'bbb:c']
    # and can also be a single string 'aa:a'
    if not isinstance(filename, (list, tuple)):
        split_files = filename.split(',')
        if all([f.endswith(YAML_EXTENSIONS) for f in split_files]):
            files = split_files  # it is a ['file.yml', ...]
        else:  # it is a single YAML string
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
    load_from_yaml(obj, files, env_list, silent, key)


def load_from_yaml(obj, files, envs, silent=True, key=None):

    for yaml_file in files:
        if yaml_file.endswith(YAML_EXTENSIONS):  # pragma: no cover
            try:
                yaml_data = yaml.load(
                    open(find_file(yaml_file, usecwd=True))
                )
            except IOError as e:
                obj.logger.debug(
                    "Unable to load YAML file {}".format(str(e)))
                yaml_data = None
            else:
                obj.logger.debug('YAML {} has been loaded'.format(yaml_file))
        else:
            # for tests it is possible to pass YAML string
            yaml_data = yaml.load(yaml_file)

        if not yaml_data:
            continue

        yaml_data = {key.lower(): value for key, value in yaml_data.items()}

        for env in envs:
            data = {}
            try:
                data = yaml_data[env.lower()]
            except KeyError:
                message = '%s env not defined in %s' % (
                    env, yaml_file)
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
