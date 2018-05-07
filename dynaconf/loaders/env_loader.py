# coding: utf-8
import os
from dynaconf.utils.parse_conf import parse_conf_data

try:
    from dotenv import load_dotenv, find_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = lambda *args, **kwargs: None  # noqa
    find_dotenv = lambda: None  # noqa


IDENTIFIER = 'env_loader'


def start_dotenv(obj):
    # load_from_dotenv_if_installed
    dotenv_path = obj.get('DOTENV_PATH_FOR_DYNACONF') or os.environ.get(
        'DOTENV_PATH_FOR_DYNACONF') or find_dotenv(usecwd=True)
    obj.logger.debug('Dotenv path %s', dotenv_path)
    load_dotenv(
        dotenv_path,
        verbose=obj.get('DOTENV_VERBOSE_FOR_DYNACONF', False),
        override=obj.get('DOTENV_OVERRIDE_FOR_DYNACONF', False)
    )


def load(obj, namespace=None, silent=True, key=None):
    default_namespace = obj.get('NAMESPACE_FOR_DYNACONF')
    # load all from default namespace (this never gets cleaned)
    load_from_env(
        IDENTIFIER,
        key,
        default_namespace,
        obj,
        silent
    )

    # rewrite with different namespace if provided
    if namespace and namespace != default_namespace:
        identifier = IDENTIFIER + '_' + namespace.lower()
        load_from_env(identifier, key, namespace, obj, silent)


def load_from_env(identifier, key, namespace, obj, silent):
    NAMESPACE = namespace.upper()  # noqa
    NAMESPACE_ = '{0}_'.format(NAMESPACE)  # noqa
    try:
        if key:
            value = os.environ.get(
                '{0}_{1}'.format(NAMESPACE, key)
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
                key.partition(NAMESPACE_)[-1]: parse_conf_data(data)
                for key, data
                in os.environ.items()
                if key.startswith(NAMESPACE_)
            }
            obj.logger.debug(
                "env_loader:loading:%s (%s)",
                data,
                identifier
            )
            obj.update(data, loader_identifier=identifier)
    except Exception as e:  # pragma: no cover
        e.message = (
            'Unable to load config env namespace ({0})'
        ).format(str(e))
        if silent:
            obj.logger.error(str(e))
        else:
            raise


def clean(obj, namespace, silent=True):  # noqa
    for identifier, data in obj.loaded_by_loaders.items():
        if identifier.startswith('env_loader'):
            for key in data:
                obj.logger.debug("cleaning: %s (%s)", key, identifier)
                obj.unset(key)
