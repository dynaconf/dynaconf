# docker run -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
# pip install hvac

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
    data = client.read(obj.VAULT_FOR_DYNACONF_PATH).get('data', {}).get('data')

    try:
        if key:
            value = parse_conf_data(data.get(key))
            if value:
                obj.set(key, value)
        else:
                obj.update(data, loader_identifier=IDENTIFIER)
    except Exception as e:
        if silent:
            if hasattr(obj, 'logger'):
                obj.logger.error(str(e))
            return False
        raise


def writer(obj, data, lease='1h'):
    client = get_client(obj)
    client.write(obj.VAULT_FOR_DYNACONF_PATH, data=data, lease=lease)
