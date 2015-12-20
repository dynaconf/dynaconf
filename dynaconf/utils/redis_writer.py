from redis import StrictRedis
from dynacong.utils.parse_conf import unparse_conf_data
from dynaconf.loaders.redis_loader import main


def write(settings, **kwargs):
    client = StrictRedis(**settings.REDIS_FOR_DYNACONF)
    for k, value in kwargs.items():
        key = "{0}_{1}".format(settings.DYNACONF_NAMESPACE, k)
        value = unparse_conf_data(value)
        client.set(key.upper(), value)
    main(settings)
