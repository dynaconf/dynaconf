# coding: utf-8
import os
import pytest
from dynaconf.utils.parse_conf import true_values


def test_deleted_raise(settings):
    """asserts variable can be deleted"""
    assert settings.TODELETE is True
    del settings.TODELETE
    with pytest.raises(AttributeError):
        assert settings.TODELETE is True
    assert settings.exists('TODELETE') is False
    assert settings.get('TODELETE') is None


def test_accepts_only_upper(settings):
    """Only upper case names are allowed
    lower case are converted"""
    assert settings.DEBUG is True
    assert settings.get('debug') is True
    assert settings.get('DEBUG') is True
    assert settings.exists('debug')
    with pytest.raises(AttributeError):
        # access in lower case is not allowed
        assert settings.debug is True


def test_call_works_as_get(settings):
    """settings.get('name') is the same as settings('name')"""

    assert settings('debug') == settings.get('DEBUG')
    assert settings('non_exist', default='hello') == 'hello'
    assert settings.get('non_exist', default='hello') == 'hello'
    assert settings.__call__('debug') == settings.DEBUG
    assert settings._wrapped.__call__('debug') == settings.DEBUG


def test_keys_are_equal(settings):
    assert set(list(settings.keys())) == set(list(settings.store.keys()))


def test_values_are_equal(settings):
    for item in settings.values():
        assert item in settings.store.values()


def test_get_env(settings):
    settings.env['FRUIT'] = 'BANANA'
    assert settings.exists_in_env('fruit') is True
    assert settings.env['FRUIT'] == settings.get_env('fruit')
    assert os.environ['FRUIT'] == settings.env.get('FRUIT')

    settings.env['SALARY'] = '180.235'
    assert settings.get_env('salary', cast='@float') == 180.235

    settings.env['ENVINT'] = '@int 24'
    assert settings.get_env('envint', cast=True) == 24


def test_float(settings):
    settings.set('money', '500.42')
    assert settings.exists('MONEY')
    assert settings.MONEY == '500.42'
    assert settings.MONEY != 500.42
    assert settings.store['MONEY'] == '500.42'
    assert 'MONEY' not in settings._deleted
    assert 'money' not in settings._deleted
    assert isinstance(settings.as_float('money'), float)
    assert settings.as_float('MONEY') == 500.42


def test_int(settings):
    settings.set('age', '500')
    assert settings.exists('AGE')
    assert settings.AGE == '500'
    assert settings.AGE != 500
    assert settings.store['AGE'] == '500'
    assert 'AGE' not in settings._deleted
    assert 'age' not in settings._deleted
    assert isinstance(settings.as_int('age'), int)
    assert settings.as_int('age') == 500


def test_bool(settings):
    for true_value in true_values:
        # ('t', 'true', 'enabled', '1', 'on', 'yes')
        settings.set('feature', true_value)
        assert settings.exists('FEATURE')
        assert settings.FEATURE == true_value
        assert settings.FEATURE is not True
        assert settings.store['FEATURE'] == true_value
        assert 'FEATURE' not in settings._deleted
        assert 'feature' not in settings._deleted
        assert isinstance(settings.as_bool('feature'), bool)
        assert settings.as_bool('FEATURE') is True

    # anything else is a false value
    false_values = ['f', 'false', 'False', 'disabled', '0', 'off', 'no']
    for false_value in false_values:
        settings.set('feature', false_value)
        assert settings.exists('FEATURE')
        assert settings.FEATURE == false_value
        assert settings.FEATURE is not False
        assert settings.store['FEATURE'] == false_value
        assert 'FEATURE' not in settings._deleted
        assert 'feature' not in settings._deleted
        assert isinstance(settings.as_bool('feature'), bool)
        assert settings.as_bool('FEATURE') is False


def test_as_json(settings):
    settings.set('fruits', '["banana", "apple", "kiwi"]')
    assert settings.exists('FRUITS')
    assert settings.FRUITS == '["banana", "apple", "kiwi"]'
    assert settings.FRUITS != ["banana", "apple", "kiwi"]
    assert settings.store['FRUITS'] == '["banana", "apple", "kiwi"]'
    assert 'FRUITS' not in settings._deleted
    assert 'fruits' not in settings._deleted
    assert isinstance(settings.as_json('fruits'), list)
    assert settings.as_json('fruits') == ["banana", "apple", "kiwi"]

    settings.set('person', '{"name": "Bruno"}')
    assert settings.exists('PERSON')
    assert settings.PERSON == '{"name": "Bruno"}'
    assert settings.PERSON != {"name": "Bruno"}
    assert settings.store['PERSON'] == '{"name": "Bruno"}'
    assert 'PERSON' not in settings._deleted
    assert 'person' not in settings._deleted
    assert isinstance(settings.as_json('person'), dict)
    assert settings.as_json('person') == {"name": "Bruno"}


def test_namespace_should_be_string(settings):
    with pytest.raises(AttributeError):
        with settings.namespace(123456):
            pass


def test_namespace_should_not_have_underline(settings):
    with pytest.raises(AttributeError):
        with settings.namespace('COOL_NAMESPACE'):
            pass


def test_path_for(settings):
    assert settings.path_for('/tmp', 'bla') == '/tmp/bla'
    assert settings.path_for('foo', 'bar', 'blaz') == './foo/bar/blaz'


def test_get_item(settings):
    assert settings['DOTENV_INT'] == 1
    assert settings['PORT'] == 5000
    with pytest.raises(KeyError):
        settings['DONOTEXISTTHISKEY']


def test_set_item(settings):
    settings['FOO'] = 'bar'
    assert settings.FOO == 'bar'
    assert 'FOO' in settings._defaults
    assert settings('FOO') == 'bar'
    assert settings.get('FOO') == 'bar'


def test_set(settings):
    # NOTE: it is recommended to call set(x, 1) or ['x'] = 1
    # instead of settings.BAZ = 'bar'
    settings.set('BAZ', 'bar')
    assert settings.BAZ == 'bar'
    assert 'BAZ' in settings._defaults
    assert settings('BAZ') == 'bar'
    assert settings.get('BAZ') == 'bar'


def test_exists(settings):
    settings.set('BOOK', 'TAOCP')
    assert settings.exists('BOOK') == True

