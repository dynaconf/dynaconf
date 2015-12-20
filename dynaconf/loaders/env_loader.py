import os
from dynaconf.utils.parse_conf import parse_conf_data


def main(obj, namespace=None, silent=True):
    namespace = namespace or getattr(
        obj, 'DYNACONF_NAMESPACE', 'DYNACONF')
    try:
        data = {
            key.partition('_')[-1]: parse_conf_data(data)
            for key, data
            in os.environ.items()
            if key.startswith(namespace)
        }
        for key, value in data.items():
            setattr(obj, key, value)
            obj.store[key] = value
    except Exception as e:
        if silent:
            return False
        e.message = 'Unable to load config env namespace (%s)' % e.message
        raise
