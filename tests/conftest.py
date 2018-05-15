# coding: utf-8
import os
import pytest

from dynaconf.base import LazySettings


@pytest.fixture(scope='module')
def settings():
    """Settings fixture with some defaults"""
    mode = 'TRAVIS' if os.environ.get('TRAVIS') else 'TEST'
    loaders = ['dynaconf.loaders.env_loader']
    os.environ['DYNA%s_HOSTNAME' % mode] = 'host.com'
    os.environ['DYNA%s_PORT' % mode] = '@int 5000'
    os.environ['DYNA%s_VALUE' % mode] = '@float 42.1'
    os.environ['DYNA%s_ALIST' % mode] = '@json ["item1", "item2", "item3"]'
    os.environ['DYNA%s_ADICT' % mode] = '@json {"key": "value"}'
    os.environ['DYNA%s_DEBUG' % mode] = '@bool true'
    os.environ['DYNA%s_TODELETE' % mode] = '@bool true'
    os.environ['PROJECT1_HOSTNAME'] = 'otherhost.com'
    sets = LazySettings(
        LOADERS_FOR_DYNACONF=loaders,
        NAMESPACE_FOR_DYNACONF="DYNA%s" % mode,
        boxed_data={
            'HOST': 'server.com',
            'port': 8080,
            'PARAMS': {
                'username': 'admin',
                'PASSWORD': 'secret',
                'token': {
                    'TYPE': 1,
                    'value': 2
                }
            }
        }
    )
    sets.SIMPLE_BOOL = False
    sets.configure()
    return sets
