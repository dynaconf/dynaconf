import os
from dynaconf.loaders.env_loader import load

os.environ['DYNACONF_HOSTNAME'] = 'host.com'
os.environ['DYNACONF_PORT'] = '@int 5000'
os.environ['DYNACONF_VALUE'] = '@float 42.1'
os.environ['DYNACONF_ALIST'] = '@json ["item1", "item2", "item3"]'
os.environ['DYNACONF_ADICT'] = '@json {"key": "value"}'
os.environ['DYNACONF_DEBUG'] = '@bool true'
os.environ['PROJECT1_HOSTNAME'] = 'otherhost.com'
os.environ['PROJECT1_PORT'] = '@int 8080'

from dynaconf import settings  # noqa
settings.configure()

def test_env_loader():
    assert settings.HOSTNAME == 'host.com'


def test_single_key():
    load(settings, namespace='PROJECT1', key='HOSTNAME')
    assert settings.HOSTNAME == 'otherhost.com'
    assert settings.PORT == 5000
