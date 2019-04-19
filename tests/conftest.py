# coding: utf-8
import os
import sys
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
    sets = LazySettings(
        LOADERS_FOR_DYNACONF=loaders,
        ENVVAR_PREFIX_FOR_DYNACONF="DYNA%s" % mode,
        ROOT_PATH_FOR_DYNACONF=os.path.dirname(os.path.abspath(__file__)),
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


@pytest.fixture(scope='module')
def testdir():
    return os.path.dirname(os.path.abspath(__file__))


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):

    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue('tmpdir')
    tmpdir.join('.env').write('DYNACONF_TESTING=true')
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))

    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield
