# coding: utf-8
import pytest
import os
from dynaconf import LazySettings
# from dynaconf.loaders.redis_loader import write


@pytest.fixture(scope='module')
def settings():
    """Settings fixture with some defaults"""
    mode = 'TRAVIS' if os.environ.get('TRAVIS') else 'TEST'
    os.environ['DYNA%s_HOSTNAME' % mode] = 'host.com'
    os.environ['DYNA%s_PORT' % mode] = '@int 5000'
    os.environ['DYNA%s_VALUE' % mode] = '@float 42.1'
    os.environ['DYNA%s_ALIST' % mode] = '@json ["item1", "item2", "item3"]'
    os.environ['DYNA%s_ADICT' % mode] = '@json {"key": "value"}'
    os.environ['DYNA%s_DEBUG' % mode] = '@bool true'
    os.environ['DYNA%s_TODELETE' % mode] = '@bool true'
    os.environ['PROJECT1_HOSTNAME'] = 'otherhost.com'
    sets = LazySettings(
        LOADERS_FOR_DYNACONF=[
            'dynaconf.loaders.env_loader',
            'dynaconf.loaders.redis_loader'
        ],
        DYNACONF_NAMESPACE="DYNA%s" % mode
    )
    sets.SIMPLE_BOOL = False
    sets.configure()
    return sets


# def pytest_runtest_setup(item):
#     # called for running each test in 'a' directory
#     print("setting up", item)  # noqa
