# coding: utf-8
import os
from dynaconf.utils.parse_conf import parse_conf_data

IDENTIFIER = 'env_loader'


def load(obj, namespace=None, silent=True, key=None):
    namespace = namespace or obj.DYNACONF_NAMESPACE
    try:
        if key:
            value = os.environ.get('%s_%s' % (namespace.upper(), key))
            if value:
                obj.set(key, value)
        else:
            data = {
                key.partition('_')[-1]: parse_conf_data(data)
                for key, data
                in os.environ.items()
                if key.startswith('%s_' % namespace.upper())
            }
            obj.update(data, loader_identifier=IDENTIFIER)
    except Exception as e:  # pragma: no cover
        e.message = 'Unable to load config env namespace (%s)' % e.message
        if silent:
            obj.logger.error(e.message)
            return False
        raise


def clean(obj, namespace, silent=True):  # noqa
    for key in obj.loaded_by_loaders.get(IDENTIFIER, {}):
        obj.unset(key)
