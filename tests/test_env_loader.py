import os
import pytest
from dynaconf.loaders.env_loader import load, clean
from dynaconf import settings  # noqa

# Default env vars
os.environ['DEFAULT_HOSTNAME'] = 'host.com'
os.environ['DEFAULT_PORT'] = '@int 5000'
os.environ['DEFAULT_ALIST'] = '@json ["item1", "item2", "item3", 123]'
os.environ['DEFAULT_ADICT'] = '@json {"key": "value", "int": 42}'
os.environ['DEFAULT_DEBUG'] = '@bool true'
os.environ['DEFAULT_MUSTBEFRESH'] = 'first'
os.environ['DEFAULT_MUSTBEALWAYSFRESH'] = 'first'
os.environ['DEFAULT_SHOULDBEFRESHINCONTEXT'] = 'first'

# CURRENT env  vars
os.environ['DEVELOPMENT_HOSTNAME'] = 'dev.otherhost.com'
os.environ['DEVELOPMENT_PORT'] = '@int 8000'

# custom env specific vars
os.environ['PROJECT1_HOSTNAME'] = 'project1.otherhost.com'
os.environ['PROJECT1_PORT'] = '@int 8080'

# GLOBAL ENV VARS
os.environ['DYNACONF_VALUE'] = '@float 42.1'

# os.environ['FRESH_VARS_FOR_DYNACONF'] = '@json ["MUSTBEALWAYSFRESH"]'
# settings.configure()
settings.configure(FRESH_VARS_FOR_DYNACONF=["MUSTBEALWAYSFRESH"])


def test_env_loader():
    assert settings.HOSTNAME == 'dev.otherhost.com'
    assert settings.PORT == 8000
    assert settings.ALIST == ["item1", "item2", "item3", 123]
    assert settings.ADICT == {"key": "value", "int": 42}


def test_single_key():
    load(settings, env='PROJECT1', key='HOSTNAME')
    # hostname is reloaded
    assert settings.HOSTNAME == 'project1.otherhost.com'
    # port still form DEVELOPMENT (current env)
    assert settings.PORT == 8000


def test_dotenv_loader():
    assert settings.DOTENV_INT == 1
    assert settings.DOTENV_STR == "hello"
    assert settings.DOTENV_FLOAT == 4.2
    assert settings.DOTENV_BOOL is False
    assert settings.DOTENV_JSON == ['1', '2']
    assert settings.DOTENV_NOTE is None


def test_dotenv_other_env_loader():
    load(settings, env='FLASK')
    assert settings.DOTENV_STR == "flask"


def test_get_fresh():
    assert settings.MUSTBEFRESH == 'first'
    os.environ['DEFAULT_MUSTBEFRESH'] = 'second'
    with pytest.raises(AssertionError):
        # fresh should now be second
        assert settings.exists('MUSTBEFRESH')
        assert settings.get_fresh('MUSTBEFRESH') == 'first'

    assert settings.get_fresh('MUSTBEFRESH') == 'second'

    os.environ['DEFAULT_THISMUSTEXIST'] = '@int 1'
    # must tnot exist yet (not loaded)
    assert settings.exists('THISMUSTEXIST') is False
    # must exist because fresh will call loaders
    assert settings.exists('THISMUSTEXIST', fresh=True) is True
    # loaders run only once
    assert settings.get('THISMUSTEXIST') == 1

    os.environ['DEFAULT_THISMUSTEXIST'] = '@int 23'
    del os.environ['DEFAULT_THISMUSTEXIST']
    # this should error because envvar got cleaned
    # but it is not, so cleaners should be fixed
    assert settings.get_fresh('THISMUSTEXIST') is None
    with pytest.raises(AttributeError):
        settings.THISMUSTEXIST
    with pytest.raises(KeyError):
        settings['THISMUSTEXIST']

    os.environ['DEFAULT_THISMUSTEXIST'] = '@int 23'
    os.environ['BLARG_THISMUSTEXIST'] = '@int 99'

    # env switch is deleting the variable
    with settings.using_env('BLARG'):
        assert settings.get('THISMUSTEXIST') == 99

    assert settings.get('THISMUSTEXIST') == 23


def test_always_fresh():
    # assert os.environ['FRESH_VARS_FOR_DYNACONF'] == '@json ["MUSTBEALWAYSFRESH"]'  # noqa
    assert settings.FRESH_VARS_FOR_DYNACONF == ["MUSTBEALWAYSFRESH"]
    assert settings.MUSTBEALWAYSFRESH == 'first'
    os.environ['DYNACONF_MUSTBEALWAYSFRESH'] = 'second'
    assert settings.MUSTBEALWAYSFRESH == 'second'
    os.environ['DYNACONF_MUSTBEALWAYSFRESH'] = 'third'
    assert settings.MUSTBEALWAYSFRESH == 'third'


def test_fresh_context():
    assert settings.SHOULDBEFRESHINCONTEXT == 'first'
    os.environ['DYNACONF_SHOULDBEFRESHINCONTEXT'] = 'second'
    assert settings.SHOULDBEFRESHINCONTEXT == 'first'
    with settings.fresh():
        assert settings.get("DOTENV_INT") == 1
        assert settings.SHOULDBEFRESHINCONTEXT == 'second'


def test_cleaner():
    clean(settings, settings.current_env)
