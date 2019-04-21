# coding: utf-8
import os
import pytest
from dynaconf.utils.parse_conf import true_values


def test_deleted_raise(settings):
    """asserts variable can be deleted"""
    assert 'TODELETE' in settings
    assert settings.TODELETE is True
    del settings.TODELETE
    with pytest.raises(AttributeError):
        assert settings.TODELETE is True
    assert settings.exists("TODELETE") is False
    assert settings.get("TODELETE") is None


def test_accepts_only_upper(settings):
    """Only upper case names are allowed
    lower case are converted"""
    assert settings.DEBUG is True
    assert settings.get("debug") is True
    assert settings.get("DEBUG") is True
    assert settings.exists("debug")
    with pytest.raises(AttributeError):
        # access in lower case is not allowed
        assert settings.debug is True


def test_populate_obj(settings):
    class Obj:
        pass

    obj = Obj()

    settings.populate_obj(obj)

    assert obj.DEBUG is True
    assert obj.VALUE == 42.1


def test_populate_obj_with_keys(settings):
    class Obj:
        pass

    obj = Obj()

    settings.populate_obj(obj, ['VALUE'])

    assert obj.VALUE == 42.1

    with pytest.raises(AttributeError):
        assert obj.DEBUG is True


def test_call_works_as_get(settings):
    """settings.get('name') is the same as settings('name')"""

    assert settings("debug") == settings.get("DEBUG")
    assert settings("non_exist", default="hello") == "hello"
    assert settings.get("non_exist", default="hello") == "hello"
    assert settings.__call__("debug") == settings.DEBUG
    assert settings._wrapped.__call__("debug") == settings.DEBUG


def test_keys_are_equal(settings):
    assert set(list(settings.keys())) == set(list(settings.store.keys()))


def test_values_are_equal(settings):
    for item in settings.values():
        assert item in settings.store.values()


def test_get_env(settings):
    settings.environ["FRUIT"] = "BANANA"
    assert settings.exists_in_environ("fruit") is True
    assert settings.environ["FRUIT"] == settings.get_environ("fruit")
    assert os.environ["FRUIT"] == settings.environ.get("FRUIT")

    settings.environ["SALARY"] = "180.235"
    assert settings.get_environ("salary", cast="@float") == 180.235

    settings.environ["ENVINT"] = "@int 24"
    assert settings.get_environ("envint", cast=True) == 24


def test_float(settings):
    settings.set("money", "500.42")
    assert settings.exists("MONEY")
    assert settings.MONEY == "500.42"
    assert settings.MONEY != 500.42
    assert settings.store["MONEY"] == "500.42"
    assert "MONEY" not in settings._deleted
    assert "money" not in settings._deleted
    assert isinstance(settings.as_float("money"), float)
    assert settings.as_float("MONEY") == 500.42


def test_int(settings):
    settings.set("age", "500")
    assert settings.exists("AGE")
    assert settings.AGE == "500"
    assert settings.AGE != 500
    assert settings.store["AGE"] == "500"
    assert "AGE" not in settings._deleted
    assert "age" not in settings._deleted
    assert isinstance(settings.as_int("age"), int)
    assert settings.as_int("age") == 500


def test_bool(settings):
    for true_value in true_values:
        # ('t', 'true', 'enabled', '1', 'on', 'yes')
        settings.set("feature", true_value)
        assert settings.exists("FEATURE")
        assert settings.FEATURE == true_value
        assert settings.FEATURE is not True
        assert settings.store["FEATURE"] == true_value
        assert "FEATURE" not in settings._deleted
        assert "feature" not in settings._deleted
        assert isinstance(settings.as_bool("feature"), bool)
        assert settings.as_bool("FEATURE") is True

    # anything else is a false value
    false_values = ["f", "false", "False", "disabled", "0", "off", "no"]
    for false_value in false_values:
        settings.set("feature", false_value)
        assert settings.exists("FEATURE")
        assert settings.FEATURE == false_value
        assert settings.FEATURE is not False
        assert settings.store["FEATURE"] == false_value
        assert "FEATURE" not in settings._deleted
        assert "feature" not in settings._deleted
        assert isinstance(settings.as_bool("feature"), bool)
        assert settings.as_bool("FEATURE") is False


def test_as_json(settings):
    settings.set("fruits", '["banana", "apple", "kiwi"]')
    assert settings.exists("FRUITS")
    assert settings.FRUITS == '["banana", "apple", "kiwi"]'
    assert settings.FRUITS != ["banana", "apple", "kiwi"]
    assert settings.store["FRUITS"] == '["banana", "apple", "kiwi"]'
    assert "FRUITS" not in settings._deleted
    assert "fruits" not in settings._deleted
    assert isinstance(settings.as_json("fruits"), list)
    assert settings.as_json("fruits") == ["banana", "apple", "kiwi"]

    settings.set("person", '{"name": "Bruno"}')
    assert settings.exists("PERSON")
    assert settings.PERSON == '{"name": "Bruno"}'
    assert settings.PERSON != {"name": "Bruno"}
    assert settings.store["PERSON"] == '{"name": "Bruno"}'
    assert "PERSON" not in settings._deleted
    assert "person" not in settings._deleted
    assert isinstance(settings.as_json("person"), dict)
    assert settings.as_json("person") == {"name": "Bruno"}


def test_env_should_be_string(settings):
    with pytest.raises(AttributeError):
        with settings.setenv(123456):
            pass


def test_env_should_not_have_underline(settings):
    with pytest.raises(AttributeError):
        with settings.setenv("COOL_env"):
            pass


def test_path_for(settings):
    assert settings.path_for(
        os.path.sep, "tmp", "bla"
    ) == os.path.join(os.path.sep, "tmp", "bla")
    assert settings.path_for(
        "foo", "bar", "blaz"
    ) == os.path.join(settings._root_path, 'foo', 'bar', 'blaz')


def test_get_item(settings):
    assert settings["DOTENV_INT"] == 1
    assert settings["PORT"] == 5000
    with pytest.raises(KeyError):
        settings["DONOTEXISTTHISKEY"]


def test_set_item(settings):
    settings["FOO"] = "bar"
    assert settings.FOO == "bar"
    assert "FOO" in settings._defaults
    assert settings("FOO") == "bar"
    assert settings.get("FOO") == "bar"


def test_set(settings):
    # NOTE: it is recommended to call set(x, 1) or ['x'] = 1
    # instead of settings.BAZ = 'bar'
    settings.set("BAZ", "bar")
    assert settings.BAZ == "bar"
    assert "BAZ" in settings._defaults
    assert settings("BAZ") == "bar"
    assert settings.get("BAZ") == "bar"


def test_global_set_merge(settings):
    settings.set("MERGE_ENABLED_FOR_DYNACONF", True)
    settings.set("MERGE_KEY", {
        "items": [{"name": "item 1"}, {"name": "item 2"}]
    })
    settings.set("MERGE_KEY", {
        "items": [{"name": "item 3"}, {"name": "item 4"}]
    })
    assert settings.MERGE_KEY == {
        "items": [
            {"name": "item 1"}, {"name": "item 2"},
            {"name": "item 3"}, {"name": "item 4"}
        ]
    }


def test_global_merge_shortcut(settings):
    settings.set("MERGE_ENABLED_FOR_DYNACONF", True)
    settings.set("MERGE_KEY", ["item1"])
    settings.set("MERGE_KEY", ["item1"])
    assert settings.MERGE_KEY == ["item1"]


def test_local_set_merge_dict(settings):
    settings.set("DATABASE", {"host": "localhost", "port": 666})
    # calling twice  does not change anything
    settings.set("DATABASE", {"host": "localhost", "port": 666})
    assert settings.DATABASE == {"host": "localhost", "port": 666}

    settings.set(
        "DATABASE",
        {"host": "new", "user": "admin", "dynaconf_merge": True}
    )
    assert settings.DATABASE == {'host': 'new', 'port': 666, 'user': 'admin'}
    assert settings.DATABASE.HOST == 'new'
    assert settings.DATABASE.user == 'admin'


def test_local_set_merge_list(settings):
    settings.set("PLUGINS", ["core"])
    settings.set("PLUGINS", ["core"])
    assert settings.PLUGINS == ["core"]

    settings.set("PLUGINS", ["debug_toolbar", "dynaconf_merge"])
    assert settings.PLUGINS == ["core", "debug_toolbar"]


def test_local_set_merge_list_unique(settings):
    settings.set("SCRIPTS", ['install.sh', 'deploy.sh'])
    settings.set("SCRIPTS", ['install.sh', 'deploy.sh'])
    assert settings.SCRIPTS == ['install.sh', 'deploy.sh']

    settings.set(
        "SCRIPTS",
        ['dev.sh', 'test.sh', 'deploy.sh', 'dynaconf_merge_unique']
    )
    assert settings.SCRIPTS == ['install.sh', 'dev.sh', 'test.sh', 'deploy.sh']


def test_exists(settings):
    settings.set('BOOK', 'TAOCP')
    assert settings.exists('BOOK') is True


def test_dotted_traversal_access(settings):
    settings.set(
        'PARAMS',
        {
            'PASSWORD': 'secret',
            'SSL': {'CONTEXT': 'SECURE'},
            'DOTTED.KEY': True
        },
        dotted_lookup=False
    )
    assert settings.get('PARAMS') == {
        'PASSWORD': 'secret',
        'SSL': {
            'CONTEXT': 'SECURE'
        },
        'DOTTED.KEY': True
    }

    assert settings('PARAMS.PASSWORD') == 'secret'
    assert settings('PARAMS.SSL.CONTEXT') == 'SECURE'
    assert settings('PARAMS.TOKEN.IMAGINARY', 1234) == 1234
    assert settings('IMAGINARY_KEY.FOO') is None
    assert settings('IMAGINARY_KEY') is None

    assert settings['PARAMS.PASSWORD'] == 'secret'
    assert settings['PARAMS.SSL.CONTEXT'] == 'SECURE'
    assert settings.PARAMS.SSL.CONTEXT == 'SECURE'

    assert settings.exists("PARAMS") is True
    assert settings.exists("PARAMS.PASSWORD") is True
    assert settings.exists("PARAMS.SSL") is True
    assert settings.exists("PARAMS.SSL.FAKE") is False
    assert settings.exists("PARAMS.SSL.CONTEXT") is True

    # Dotted traversal should not work for dictionary-like key access.
    with pytest.raises(KeyError):
        settings['PARAMS.DOESNOTEXIST']

    # Disable dot-traversal on a per-call basis.
    assert settings('PARAMS.PASSWORD', dotted_lookup=False) is None

    assert settings('PARAMS.DOTTED.KEY') is None
    assert settings('PARAMS').get('DOTTED.KEY') is True

    settings.set('DOTTED.KEY', True, dotted_lookup=False)
    assert settings('DOTTED.KEY', dotted_lookup=False) is True

    settings.set(
        'NESTED_1',
        {
            "nested_2": {
                "nested_3": {
                    "nested_4": True
                }
            }
        }
    )

    assert settings.NESTED_1.nested_2.nested_3.nested_4 is True
    assert settings['NESTED_1.nested_2.nested_3.nested_4'] is True
    assert settings('NESTED_1.nested_2.nested_3.nested_4') is True
    # First key is always transformed to upper()
    assert settings('nested_1.nested_2.nested_3.nested_4') is True


def test_dotted_set(settings):

    settings.set('nested_1.nested_2.nested_3.nested_4', 'secret')

    assert settings.NESTED_1.NESTED_2.NESTED_3.NESTED_4 == 'secret'
    assert settings.NESTED_1.NESTED_2.NESTED_3.to_dict() == {'nested_4': 'secret'}
    assert settings.NESTED_1.NESTED_2.to_dict() == {
        'nested_3': {
            'nested_4': 'secret'
        }
    }

    assert settings.get('nested_1').to_dict() == {
        'nested_2': {
            'nested_3': {
                'nested_4': 'secret'
            }
        }
    }

    with pytest.raises(KeyError):
        settings.NESTED_1.NESTED_5


def test_dotted_set_with_merge(settings):
    settings.set("MERGE_ENABLED_FOR_DYNACONF", True)

    settings.set("MERGE.KEY", {
        "items": [{"name": "item 1"}, {"name": "item 2"}]
    })
    settings.set("MERGE.KEY", {
        "items": [{"name": "item 3"}, {"name": "item 4"}]
    })

    assert settings.MERGE.KEY == {
        'items': [
            {'name': 'item 1'},
            {'name': 'item 2'},
            {'name': 'item 3'},
            {'name': 'item 4'},
        ]
    }
