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
    redis = StrictRedis(**obj.get('REDIS_FOR_DYNACONF'))
    namespace = namespace or obj.current_namespace
    holder = "DYNACONF_%s" % namespace
    try:
        if key:
            value = redis.hget(holder.upper(), key)
            if value:
                parsed_value = parse_conf_data(value)
                if parsed_value:
                    obj.set(key, parsed_value)
        else:
            data = {
                key: parse_conf_data(value)
                for key, value in redis.hgetall(holder.upper()).items()
            }
            if data:
                obj.update(data, loader_identifier=IDENTIFIER)
    except Exception as e:
        if silent:
            if hasattr(obj, 'logger'):
                obj.logger.error(str(e))
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


def write(obj, data=None, **kwargs):
    """
    Write a value in to loader source
    :param obj: settings object
    :param data: vars to be stored
    :param kwargs: vars to be stored
    :return:
    """
    client = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    holder = "DYNACONF_%s" % obj.current_namespace
    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError('Data must be provided')
    redis_data = {
        key.upper(): unparse_conf_data(value)
        for key, value in data.items()
    }
    client.hmset(holder.upper(), redis_data)
    load(obj)


def delete(obj, key=None):
    """
    Delete a single key if specified, or all namespace if key is none
    :param obj: settings object
    :param key: key to delete from store location
    :return: None
    """
    client = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    holder = "DYNACONF_%s" % obj.current_namespace
    if key:
        client.hdel(holder.upper(), key.upper())
        obj.unset(key)
    else:
        keys = client.hkeys(holder.upper())
        client.delete(holder.upper())
        obj.unset_all(keys)
