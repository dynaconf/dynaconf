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

    namespace = namespace or obj.get('DYNACONF_NAMESPACE')

    # clean(obj, namespace, identifier=filename)

    # can be a filename settings.yml
    # can be a multiple fileset settings1.yml, settings2.yaml etc
    # and also a list of strings ['aaa:a', 'bbb:c']
    # and can also be a single string 'aa:a'
    if not isinstance(filename, (list, tuple)):
        split_files = filename.split(',')
        if all([f.endswith(('.yaml', '.yml')) for f in split_files]):
            files = split_files  # it is a ['file.yml', ...]
        else:  # it is a single YAML string
            files = [filename]
    else:  # it is already a list/tuple
        files = filename

    for yaml_file in files:
        if yaml_file.endswith(('.yaml', '.yml')):  # pragma: no cover
            yaml_data = yaml.load(open(yaml_file))
        else:
            # for tests it is possible to pass YAML string
            yaml_data = yaml.load(yaml_file)

        if not yaml_data and silent:
            continue

        yaml_data = {key.lower(): value for key, value in yaml_data.items()}

        # ---->
        # Load from namespace_filename.yaml

        data = {}
        try:
            data = yaml_data[namespace.lower()]
        except KeyError:
            if silent:
                if hasattr(obj, 'logger'):
                    obj.logger.debug(
                        '%s namespace not defined in yaml source' % namespace
                    )
            else:
                raise KeyError(
                    '%s namespace not defined in %s' % (namespace, filename)
                )

        if namespace and namespace != obj.get('DYNACONF_NAMESPACE'):
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
