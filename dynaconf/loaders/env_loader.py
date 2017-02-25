# coding: utf-8
import os
from dynaconf.utils.parse_conf import parse_conf_data

IDENTIFIER = 'env_loader'


def load(obj, namespace=None, silent=True, key=None):

    # load all from default namespace (this never gets cleaned)
    load_from_env(IDENTIFIER, key, obj.DYNACONF_NAMESPACE, obj, silent)

    # rewrite with different namespace if provided
    if namespace and namespace != obj.DYNACONF_NAMESPACE:
        identifier = IDENTIFIER + '_' + namespace.lower()
        load_from_env(identifier, key, namespace, obj, silent)


def load_from_env(identifier, key, namespace, obj, silent):
    try:
        if key:
            value = os.environ.get(
                '{0}_{1}'.format(namespace.upper(), key)
            )
            if value:
                obj.set(key, value, loader_identifier=identifier)
        else:
            data = {
                key.partition('_')[-1]: parse_conf_data(data)
                for key, data
                in os.environ.items()
                if key.startswith('{0}_'.format(namespace.upper()))
            }
            obj.update(data, loader_identifier=identifier)
    except Exception as e:  # pragma: no cover
        e.message = (
            'Unable to load config env namespace ({0})'
        ).format(e.message)
        if silent:
            obj.logger.error(e.message)
        else:
            raise


def clean(obj, namespace, silent=True):  # noqa
    for identifier, data in obj.loaded_by_loaders.items():
        if identifier.startswith('env_loader_'):
            for key in data:
                obj.unset(key)
