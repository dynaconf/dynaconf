# coding: utf-8
import os
from dynaconf.utils.parse_conf import parse_conf_data

IDENTIFIER = 'env_loader'


def load(obj, env=None, silent=True, key=None):
    default_env = obj.get('DEFAULT_ENV_FOR_DYNACONF')
    global_env = obj.get('GLOBAL_ENV_FOR_DYNACONF')

    # load all from default env
    load_from_env(
        IDENTIFIER,
        key,
        default_env,
        obj,
        silent
    )

    # rewrite with current env if provided
    env = env or obj.current_env
    if env and env != default_env and env != global_env:
        identifier = IDENTIFIER + '_' + env.lower()
        load_from_env(identifier, key, env, obj, silent)

    # Load the global env if exists and overwrite everything
    load_from_env(
        IDENTIFIER + '_global',
        key,
        global_env,
        obj,
        silent
    )


def load_from_env(identifier, key, env, obj, silent):
    env = env.upper()  # noqa
    env_ = '{0}_'.format(env)  # noqa
    try:
        if key:
            value = os.environ.get(
                '{0}_{1}'.format(env, key)
            )
            if value:
                obj.logger.debug(
                    "env_loader:loading by key: %s:%s (%s)",
                    key,
                    value,
                    identifier
                )
                obj.set(key, value, loader_identifier=identifier)
        else:
            data = {
                key.partition(env_)[-1]: parse_conf_data(data)
                for key, data
                in os.environ.items()
                if key.startswith(env_)
            }
            obj.logger.debug(
                "env_loader:loading:%s (%s)",
                data,
                identifier
            )
            obj.update(data, loader_identifier=identifier)
    except Exception as e:  # pragma: no cover
        e.message = (
            'Unable to load config env env ({0})'
        ).format(str(e))
        if silent:
            obj.logger.error(str(e))
        else:
            raise
