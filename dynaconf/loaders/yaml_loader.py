# coding: utf-8
try:
    import yaml
except ImportError as e:  # pragma: no cover
    yaml = None

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
        raise RuntimeError(
            "PyYAML package is not installed in your environment.\n"
            "To use this loader you have to install it with\n"
            "pip install PyYAML\n"
            "or\n"
            "pip install dynaconf[yaml]"
        )

    filename = filename or obj.get('YAML')
    if not filename:
        return

    namespace = namespace or obj.DYNACONF_NAMESPACE

    # clean(obj, namespace, identifier=filename)

    if filename.endswith(('.yaml', '.yml')):  # pragma: no cover
        yaml_data = yaml.load(open(filename))
    else:
        # for tests it is possible to pass YAML string
        yaml_data = yaml.load(filename)

    yaml_data = {key.lower(): value for key, value in yaml_data.items()}

    # ---->
    # Load from namescape_settings.yaml

    try:
        data = yaml_data[namespace.lower()]
    except KeyError:
        raise KeyError(
            '%s namespace not defined in %s' % (namespace, filename)
        )

    if namespace and namespace != obj.DYNACONF_NAMESPACE:
        identifier = "{0}_{1}".format(IDENTIFIER, namespace.lower())
    else:
        identifier = IDENTIFIER

    if not key:
        obj.update(data, loader_identifier=identifier)
    else:
        obj.set(key, data.get(key), loader_identifier=identifier)


def clean(obj, namespace, silent=True):  # noqa
    for identifier, data in obj.loaded_by_loaders.items():
        if identifier.startswith('yam_loader_'):
            for key in data:
                obj.unset(key)
