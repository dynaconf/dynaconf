# docker run -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
# pip install hvac

from hvac import Client


def load(obj, namespace=None, silent=None, key=None):
    client = Client(token='myroot')
    client.is_authenticated()
    client.write('/secret/data/dynaconf', data={'zaz': 'bar'}, lease='1h')
    client.read('/secret/data/dynaconf').get('data', {}).get('data')
