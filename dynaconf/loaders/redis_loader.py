# coding: utf-8
from dynaconf.utils.parse_conf import parse_conf_data, unparse_conf_data
try:
    from redis import StrictRedis
except ImportError as e:
    raise ImportError(
        "redis package is not installed in your environment.\n"
        "To use this loader you have to install it with\n"
        "pip install redis\n"
        "or\n"
        "pip install dynaconf[redis]"
    )

IDENTIFIER = 'redis_loader'


def load(obj, namespace=None, silent=True, key=None):
    """
    Reads and loads in to "settings" a single key or all keys from redis
    :param obj: the settings instance
    :param namespace: settings namespace default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in namespace
    :return: None
    """
    redis = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    namespace = namespace or obj.DYNACONF_NAMESPACE
    holder = "DYNACONF_%s" % namespace
    try:
        if key:
            value = parse_conf_data(redis.hget(holder.upper(), key))
            if value:
                obj.set(key, value)
        else:
            data = {
                key: parse_conf_data(value)
                for key, value in redis.hgetall(holder.upper()).items()
            }
            if data:
                obj.update(data, loader_identifier=IDENTIFIER)
    except Exception as e:
        e.message = 'Unable to load config from redis (%s)' % e.message
        if silent:
            obj.logger.error(e.message)
            return False
        raise


def clean(obj, namespace, silent=True):  # noqa
    """
    After a load, all loaded vars are stored at loaded_by_loaders
    clean should clean only the loaded vars.
    :param obj: the settings instance
    :param namespace: settings namespace default='DYNACONF'
    :param silent: if errors should raise
    :return:
    """
    for key in obj.loaded_by_loaders.get(IDENTIFIER, {}):
        obj.unset(key)


def write(obj, **kwargs):
    """
    Write a value in to loader source
    :param obj: settings object
    :param kwargs: vars to be stored
    :return:
    """
    client = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    holder = "DYNACONF_%s" % obj.DYNACONF_NAMESPACE
    data = {
        key.upper(): unparse_conf_data(value)
        for key, value in kwargs.items()
    }
    client.hmset(holder.upper(), data)
    load(obj)


def delete(obj, key=None):
    """
    Delete a single key if specified, or all namespace if key is none
    :param obj: settings object
    :param key: key to delete from store location
    :return: None
    """
    client = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    holder = "DYNACONF_%s" % obj.DYNACONF_NAMESPACE
    if key:
        client.hdel(holder.upper(), key.upper())
        obj.unset(key)
    else:
        keys = client.hkeys(holder.upper())
        client.delete(holder.upper())
        obj.unset_all(keys)
