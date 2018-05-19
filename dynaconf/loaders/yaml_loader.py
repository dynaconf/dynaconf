# coding: utf-8
from dynaconf.constants import YAML_EXTENSIONS
try:
    import yaml
except ImportError as e:  # pragma: no cover
    yaml = None

from dynaconf.utils.files import find_file

IDENTIFIER = 'yaml_loader'


def load(obj, namespace=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "settings" a single key or all keys from yaml file
    :param obj: the settings instance
    :param namespace: settings namespace default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in namespace
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

    namespace = namespace or obj.current_namespace

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

    # load
    namespace_list = [obj.get('BASE_NAMESPACE_FOR_DYNACONF')]
    if namespace and namespace not in namespace_list:
        namespace_list.append(namespace)
    load_from_yaml(obj, files, namespace_list, silent, key)


def load_from_yaml(obj, files, namespaces, silent=True, key=None):

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

        for namespace in namespaces:
            data = {}
            try:
                data = yaml_data[namespace.lower()]
            except KeyError:
                message = '%s namespace not defined in %s' % (
                    namespace, yaml_file)
                if silent:
                    obj.logger.warning(message)
                else:
                    raise KeyError(message)

            if namespace != obj.get('BASE_NAMESPACE_FOR_DYNACONF'):
                identifier = "{0}_{1}".format(IDENTIFIER, namespace.lower())
            else:
                identifier = IDENTIFIER

            if not key:
                obj.update(data, loader_identifier=identifier)
            else:
                obj.set(key, data.get(key), loader_identifier=identifier)


def clean(obj, namespace, silent=True):  # noqa
    for identifier, data in obj.loaded_by_loaders.items():
        if identifier.startswith('yaml_loader'):
            for key in data:
                obj.logger.debug("cleaning: %s (%s)", key, identifier)
                obj.unset(key)
