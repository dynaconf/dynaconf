import os
from dynaconf.utils.parse_conf import parse_conf_data

IDENTIFIER = 'env_loader'


def load(obj, namespace=None, silent=True):
    namespace = namespace or obj.DYNACONF_NAMESPACE
    try:
        data = {
            key.partition('_')[-1]: parse_conf_data(data)
            for key, data
            in os.environ.items()
            if key.startswith('%s_' % namespace)
        }
        obj.loaded_by_loaders[IDENTIFIER] = data
        for key, value in data.items():
            obj.set(key, value)
    except Exception as e:
        e.message = 'Unable to load config env namespace (%s)' % e.message
        if silent:
            obj.logger.error(e.message)
            return False
        raise


def clean(obj, namespace, silent=True):
    for key in obj.loaded_by_loaders.get(IDENTIFIER, {}):
        obj.unset(key)
