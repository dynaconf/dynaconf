# docker run -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
# pip install hvac

import os
from hvac import Client
from dynaconf.utils.parse_conf import parse_conf_data

IDENTIFIER = 'vault'


def get_client(obj):
    client = Client(
        **{k: v for k, v in obj.VAULT_FOR_DYNACONF.items() if v is not None}
    )
    assert client.is_authenticated(), "Vault authentication error"
    return client


def load(obj, env=None, silent=None, key=None):
    client = get_client(obj)
    holder = obj.get('GLOBAL_ENV_FOR_DYNACONF')
    path = os.path.join(obj.VAULT_FOR_DYNACONF_PATH, holder.lower())
    data = client.read(path)
    if data:
        data = data.get('data', {}).get('data')

    try:
        if data and key:
            value = parse_conf_data(data.get(key), tomlfy=True)
            if value:
                obj.set(key, value)
        elif data:
            obj.update(data, loader_identifier=IDENTIFIER, tomlfy=True)
    except Exception as e:
        if silent:
            if hasattr(obj, 'logger'):
                obj.logger.error(str(e))
            return False
        raise


def write(obj, data=None, lease='1h', **kwargs):
    """
    Write a value in to loader source
    :param obj: settings object
    :param data: vars to be stored
    :param kwargs: vars to be stored
    :return:
    """
    if obj.VAULT_FOR_DYNACONF_ENABLED is False:
        raise RuntimeError(
            'Vault is not configured \n'
            'export VAULT_FOR_DYNACONF_ENABLED=true\n'
            'and configure the VAULT_FOR_DYNACONF_* variables'
        )
    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError('Data must be provided')
    client = get_client(obj)
    path = os.path.join(
        obj.VAULT_FOR_DYNACONF_PATH,
        obj.get('GLOBAL_ENV_FOR_DYNACONF').lower()
    )
    client.write(path, data=data, lease=lease)
    load(obj)
