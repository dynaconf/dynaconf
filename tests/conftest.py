# coding: utf-8
import pytest
import os
from dynaconf import LazySettings
from dynaconf.loaders.redis_loader import write


@pytest.fixture(scope='module')
def settings():
    mode = 'TRAVIS' if os.environ.get('TRAVIS') else 'TEST'
    return LazySettings(
        LOADERS_FOR_DYNACONF=[
            'dynaconf.loaders.env_loader',
            'dynaconf.loaders.redis_loader'
        ],
        DYNACONF_NAMESPACE="DYNA%s" % mode
    )

def pytest_runtest_setup(item):
    # called for running each test in 'a' directory
    print("setting up", item)