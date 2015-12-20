from redis import StrictRedis
from dynaconf.utils.parse_conf import parse_conf_data


def main(obj, namespace=None, silent=True):
    redis = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    namespace = namespace or obj.DYNACONF_NAMESPACE
    try:
        data = {
            key.partition('_')[-1]: parse_conf_data(redis.get(key))
            for key in redis.keys('%s*' % namespace)
        }
        for key, value in data.items():
            setattr(obj, key, value)
            obj.store[key] = value
    except Exception as e:
        if silent:
            return False
        e.message = 'Unable to load config from redis (%s)' % e.message
        raise
