# coding: utf-8
from dynaconf.constants import JSON_EXTENSIONS
import json
from dynaconf.utils.files import find_file

IDENTIFIER = 'json_loader'


def load(obj, namespace=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "settings" a single key or all keys from json file
    :param obj: the settings instance
    :param namespace: settings namespace default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in namespace
    :return: None
    """
    filename = filename or obj.get('JSON')
    if not filename:
        return

    namespace = namespace or obj.current_namespace

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

    # load
    namespace_list = [obj.get('BASE_NAMESPACE_FOR_DYNACONF')]
    # import ipdb; ipdb.set_trace()
    if namespace and namespace not in namespace_list:
        namespace_list.append(namespace)
    load_from_json(obj, files, namespace_list, silent, key)


def load_from_json(obj, files, namespaces, silent=True, key=None):

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

        for namespace in namespaces:

            data = {}
            try:
                data = json_data[namespace.lower()]
            except KeyError:
                message = '%s namespace not defined in %s' % (
                    namespace, json_file)
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
        if identifier.startswith('json_loader'):
            for key in data:
                obj.logger.debug("cleaning: %s (%s)", key, identifier)
                obj.unset(key)
