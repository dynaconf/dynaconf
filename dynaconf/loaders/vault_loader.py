# docker run -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
# pip install hvac

import os
from hvac import Client
from dynaconf.utils.parse_conf import parse_conf_data

IDENTIFIER = 'vault_loader'


def get_client(obj):
    client = Client(
        **{k: v for k, v in obj.VAULT_FOR_DYNACONF.items() if v is not None}
    )
    assert client.is_authenticated(), "Vault authentication error"
    return client


def load(obj, namespace=None, silent=None, key=None):
    client = get_client(obj)
    namespace = namespace or obj.current_namespace
    path = os.path.join(obj.VAULT_FOR_DYNACONF_PATH, namespace.lower())
    data = client.read(path)
    if data:
        data = data.get('data', {}).get('data')

    try:
        if data and key:
            value = parse_conf_data(data.get(key))
            if value:
                obj.set(key, value)
        elif data:
            obj.update(data, loader_identifier=IDENTIFIER)
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
    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError('Data must be provided')
    client = get_client(obj)
    path = os.path.join(
        obj.VAULT_FOR_DYNACONF_PATH,
        obj.current_namespace.lower()
    )
    client.write(path, data=data, lease=lease)
    load(obj)
