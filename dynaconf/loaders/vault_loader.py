# docker run -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
# pip install hvac

import os
from dynaconf.utils.parse_conf import parse_conf_data

try:
    from hvac import Client
except ImportError as e:
    raise ImportError(
        "vault package is not installed in your environment. "
        "`pip install dynaconf[vault]` or disable the vault loader with "
        "export VAULT_ENABLED_FOR_DYNACONF=false"
    )


IDENTIFIER = 'vault'


def get_client(obj):
    client = Client(
        **{k: v for k, v in obj.VAULT_FOR_DYNACONF.items() if v is not None}
    )
    assert client.is_authenticated(), (
        "Vault authentication error is VAULT_TOKEN_FOR_DYNACONF defined?"
    )
    return client


def load(obj, env=None, silent=None, key=None):
    """Reads and loads in to "settings" a single key or all keys from vault

    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :return: None
    """

    client = get_client(obj)
    holder = obj.get('GLOBAL_ENV_FOR_DYNACONF')
    path = os.path.join(obj.VAULT_PATH_FOR_DYNACONF, holder.lower())
    data = client.read(path)
    if data:
        data = data.get('data', {}).get('data')

    try:
        if data and key:
            value = parse_conf_data(data.get(key), tomlfy=True)
            if value:
                obj.logger.debug(
                    "vault_loader: loading by key: %s:%s (%s:%s)",
                    key,
                    '****',
                    IDENTIFIER,
                    holder
                )
                obj.set(key, value)
        elif data:
            obj.logger.debug(
                "vault_loader: loading: %s (%s:%s)",
                list(data.keys()),
                IDENTIFIER,
                holder
            )
            obj.update(data, loader_identifier=IDENTIFIER, tomlfy=True)
    except Exception as e:
        if silent:
            if hasattr(obj, 'logger'):
                obj.logger.error(str(e))
            return False
        raise


def write(obj, data=None, lease='1h', **kwargs):
    """Write a value in to loader source

    :param obj: settings object
    :param data: vars to be stored
    :param kwargs: vars to be stored
    :return:
    """
    if obj.VAULT_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError(
            'Vault is not configured \n'
            'export VAULT_ENABLED_FOR_DYNACONF=true\n'
            'and configure the VAULT_FOR_DYNACONF_* variables'
        )
    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError('Data must be provided')
    client = get_client(obj)
    path = os.path.join(
        obj.VAULT_PATH_FOR_DYNACONF,
        obj.get('GLOBAL_ENV_FOR_DYNACONF').lower()
    )
    client.write(path, data=data, lease=lease)
    load(obj)
