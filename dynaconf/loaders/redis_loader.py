from redis import StrictRedis
from dynaconf.utils.parse_conf import parse_conf_data

IDENTIFIER = 'redis_loader'


def load(obj, namespace=None, silent=True):
    redis = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    namespace = namespace or obj.DYNACONF_NAMESPACE
    try:
        data = {
            key.partition('_')[-1]: parse_conf_data(redis.get(key))
            for key in redis.keys('%s_*' % namespace)
        }
        obj.loaded_by_loaders[IDENTIFIER] = data
        for key, value in data.items():
            obj.set(key, value)
    except Exception as e:
        e.message = 'Unable to load config from redis (%s)' % e.message
        if silent:
            obj.logger.error(e.message)
            return False
        raise


def clean(obj, namespace, silent=True):
    for key in obj.loaded_by_loaders.get(IDENTIFIER, {}):
        obj.unset(key)
