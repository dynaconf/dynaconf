from redis import StrictRedis
from dynaconf.utils.parse_conf import unparse_conf_data
from dynaconf.loaders.redis_loader import load


def write(settings, **kwargs):
    client = StrictRedis(**settings.REDIS_FOR_DYNACONF)
    for k, value in kwargs.items():
        key = "{0}_{1}".format(settings.DYNACONF_NAMESPACE, k)
        value = unparse_conf_data(value)
        client.set(key.upper(), value)
    load(settings)


def delete(settings, key):
    client = StrictRedis(**settings.REDIS_FOR_DYNACONF)
    key = "{0}_{1}".format(settings.DYNACONF_NAMESPACE, key)
    client.delete(key)
