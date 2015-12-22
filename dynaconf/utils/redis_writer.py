from redis import StrictRedis
from dynaconf.utils.parse_conf import unparse_conf_data
from dynaconf.loaders.redis_loader import load


def write(settings, **kwargs):
    client = StrictRedis(**settings.REDIS_FOR_DYNACONF)
    holder = "DYNACONF_%s" % settings.DYNACONF_NAMESPACE
    data = {
        key.upper(): unparse_conf_data(value)
        for key, value in kwargs.items()
    }
    client.hmset(holder, data)
    load(settings)


def delete(settings, key):
    client = StrictRedis(**settings.REDIS_FOR_DYNACONF)
    holder = "DYNACONF_%s" % settings.DYNACONF_NAMESPACE
    client.hdel(holder, key.upper())
    settings.unset(key)
