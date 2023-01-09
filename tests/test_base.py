from __future__ import annotations

import os

import pytest

from dynaconf import Dynaconf
from dynaconf import LazySettings
from dynaconf.loaders import toml_loader
from dynaconf.loaders import yaml_loader
from dynaconf.strategies.filtering import PrefixFilter
from dynaconf.utils.parse_conf import true_values
from dynaconf.vendor.box.box_list import BoxList


def test_deleted_raise(settings):
    """asserts variable can be deleted"""
    assert "TODELETE" in settings
    assert settings.TODELETE is True
    del settings.TODELETE
    with pytest.raises(AttributeError):
        assert settings.TODELETE is True
    assert settings.exists("TODELETE") is False
    assert settings.get("TODELETE") is None


def test_delete_and_set_again(settings):
    """asserts variable can be deleted and set again"""

    # set
    settings.TODELETE2 = True
    assert "TODELETE2" in settings
    assert settings.TODELETE2 is True

    # delete
    del settings.TODELETE2
    assert settings.exists("TODELETE2") is False
    assert settings.get("TODELETE2") is None

    # set again
    settings.TODELETE2 = "new value"
    assert settings.TODELETE2 == "new value"


def test_accepts_only_upper():
    """Only upper case names are allowed if lowercase_read=False
    lower case are converted"""

    settings = LazySettings(debug=True, lowercase_read=False)

    assert settings.DEBUG is True
    assert settings.get("debug") is True
    assert settings.get("DEBUG") is True
    assert settings.get("Debug") is True
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

    settings.populate_obj(obj, ["VALUE"])

    assert obj.VALUE == 42.1

    with pytest.raises(AttributeError):
        assert obj.DEBUG is True


def test_populate_obj_with_ignore(settings):
    class Obj:
        pass

    obj = Obj()

    settings.populate_obj(obj, ignore=["VALUE"])

    assert obj.DEBUG is True

    with pytest.raises(AttributeError):
        assert obj.VALUE == 42.1


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
    with pytest.raises(ValueError):
        settings.setenv(123456)


def test_env_should_not_have_underline(settings):
    with pytest.raises(ValueError):
        settings.setenv("COOL_env")


def test_path_for(settings):
    assert settings.path_for(os.path.sep, "tmp", "bla") == os.path.join(
        os.path.sep, "tmp", "bla"
    )
    assert settings.path_for("foo", "bar", "blaz") == os.path.join(
        settings._root_path, "foo", "bar", "blaz"
    )


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
    settings.set(
        "MERGE_KEY", {"items": [{"name": "item 1"}, {"name": "item 2"}]}
    )
    settings.set(
        "MERGE_KEY", {"items": [{"name": "item 3"}, {"name": "item 4"}]}
    )
    assert settings.MERGE_KEY == {
        "items": [
            {"name": "item 1"},
            {"name": "item 2"},
            {"name": "item 3"},
            {"name": "item 4"},
        ]
    }


def test_global_merge_shortcut(settings):
    settings.set("MERGE_ENABLED_FOR_DYNACONF", True)
    settings.set("MERGE_KEY", ["item1"])
    settings.set("MERGE_KEY", ["item1"])
    assert settings.MERGE_KEY == ["item1"]


def test_local_set_merge_dict():
    settings = Dynaconf()
    settings.set("DATABASE", {"host": "localhost", "port": 666})
    # calling twice  does not change anything
    settings.set("DATABASE", {"host": "localhost", "port": 666})
    assert settings.DATABASE == {"host": "localhost", "port": 666}

    settings.set(
        "DATABASE", {"host": "new", "user": "admin", "dynaconf_merge": True}
    )
    assert settings.DATABASE == {"host": "new", "port": 666, "user": "admin"}
    assert settings.DATABASE.HOST == "new"
    assert settings.DATABASE.user == "admin"

    settings.set("DATABASE.attrs", {"a": ["b", "c"]})
    settings.set("DATABASE.attrs", {"dynaconf_merge": {"foo": "bar"}})
    assert settings.DATABASE.attrs == {"a": ["b", "c"], "foo": "bar"}

    settings.set("DATABASE.attrs", {"yeah": "baby", "dynaconf_merge": True})
    assert settings.DATABASE.attrs == {
        "a": ["b", "c"],
        "foo": "bar",
        "yeah": "baby",
    }

    settings.set(
        "DATABASE.attrs",
        {"a": ["d", "e", "dynaconf_merge"], "dynaconf_merge": True},
    )

    assert settings.DATABASE.attrs == {
        "a": ["b", "c", "d", "e"],
        "foo": "bar",
        "yeah": "baby",
    }

    settings.set("DATABASE.attrs.a", ["d", "e", "f", "dynaconf_merge_unique"])
    assert settings.DATABASE.attrs.a == ["b", "c", "d", "e", "f"]


def test_local_set_merge_list(settings):
    settings.set("PLUGINS", ["core"])
    settings.set("PLUGINS", ["core"])
    assert settings.PLUGINS == ["core"]

    settings.set("PLUGINS", ["debug_toolbar", "dynaconf_merge"])
    assert settings.PLUGINS == ["core", "debug_toolbar"]


def test_local_set_merge_list_unique(settings):
    settings.set("SCRIPTS", ["install.sh", "deploy.sh"])
    settings.set("SCRIPTS", ["install.sh", "deploy.sh"])
    assert settings.SCRIPTS == ["install.sh", "deploy.sh"]

    settings.set(
        "SCRIPTS", ["dev.sh", "test.sh", "deploy.sh", "dynaconf_merge_unique"]
    )
    assert settings.SCRIPTS == ["install.sh", "dev.sh", "test.sh", "deploy.sh"]


def test_set_explicit_merge_token(tmpdir):
    data = {
        "a_list": [1, 2],
        "b_list": [1],
        "a_dict": {"name": "Bruno"},
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data, merge=False)
    settings = LazySettings(settings_file="settings.toml")
    assert settings.A_LIST == [1, 2]
    assert settings.B_LIST == [1]
    assert settings.A_DICT == {"name": "Bruno"}
    assert settings.A_DICT.name == "Bruno"

    settings.set("a_list", [3], merge=True)
    assert settings.A_LIST == [1, 2, 3]

    settings.set("b_list", "@merge [2]")
    assert settings.B_LIST == [1, 2]

    settings.set("b_list", "@merge [3, 4]")
    assert settings.B_LIST == [1, 2, 3, 4]

    settings.set("b_list", "@merge 5")
    assert settings.B_LIST == [1, 2, 3, 4, 5]

    settings.set("b_list", "@merge 6.6")
    assert settings.B_LIST == [1, 2, 3, 4, 5, 6.6]

    settings.set("b_list", "@merge false")
    assert settings.B_LIST == [1, 2, 3, 4, 5, 6.6, False]

    settings.set("b_list", "@merge foo,bar")
    assert settings.B_LIST == [1, 2, 3, 4, 5, 6.6, False, "foo", "bar"]

    settings.set("b_list", "@merge zaz")
    assert settings.B_LIST == [1, 2, 3, 4, 5, 6.6, False, "foo", "bar", "zaz"]

    settings.set("a_dict", "@merge {city='Guarulhos'}")
    assert settings.A_DICT.name == "Bruno"
    assert settings.A_DICT.city == "Guarulhos"

    settings.set("a_dict", "@merge country=Brasil")
    assert settings.A_DICT.name == "Bruno"
    assert settings.A_DICT.city == "Guarulhos"
    assert settings.A_DICT.country == "Brasil"

    settings.set("new_key", "@merge foo=bar")
    assert settings.NEW_KEY == {"foo": "bar"}


def test_set_new_merge_issue_241_1(tmpdir):
    data = {
        "default": {
            "name": "Bruno",
            "colors": ["red", "green"],
            "data": {
                "links": {"twitter": "rochacbruno", "site": "brunorocha.org"}
            },
        }
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data, merge=False)
    settings = LazySettings(environments=True, settings_file="settings.toml")
    assert settings.NAME == "Bruno"
    assert settings.COLORS == ["red", "green"]
    assert settings.DATA.links == {
        "twitter": "rochacbruno",
        "site": "brunorocha.org",
    }


def test_set_new_merge_issue_241_2(tmpdir):
    data = {
        "default": {
            "name": "Bruno",
            "colors": ["red", "green"],
            "data": {
                "links": {"twitter": "rochacbruno", "site": "brunorocha.org"}
            },
        }
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data, merge=False)

    data = {
        "dynaconf_merge": True,
        "default": {
            "colors": ["blue"],
            "data": {"links": {"github": "rochacbruno.github.io"}},
        },
    }
    toml_loader.write(
        str(tmpdir.join("settings.local.toml")), data, merge=False
    )

    settings = LazySettings(environments=True, settings_file="settings.toml")
    assert settings.NAME == "Bruno"
    assert settings.COLORS == ["red", "green", "blue"]
    assert settings.DATA.links == {
        "twitter": "rochacbruno",
        "site": "brunorocha.org",
        "github": "rochacbruno.github.io",
    }


def test_set_new_merge_issue_241_3(tmpdir):
    data = {
        "name": "Bruno",
        "colors": ["red", "green"],
        "data": {
            "links": {"twitter": "rochacbruno", "site": "brunorocha.org"}
        },
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data, merge=False)

    data = {
        "name": "Tommy Shelby",
        "colors": {"dynaconf_merge": ["yellow", "pink"]},
        "data": {"links": {"site": "pb.com"}},
    }
    toml_loader.write(
        str(tmpdir.join("settings.local.toml")), data, merge=False
    )

    settings = LazySettings(settings_file="settings.toml")
    assert settings.NAME == "Tommy Shelby"
    assert settings.COLORS == ["red", "green", "yellow", "pink"]
    assert settings.DATA.links == {"site": "pb.com"}


def test_set_new_merge_issue_241_4(tmpdir):
    data = {
        "name": "Bruno",
        "colors": ["red", "green"],
        "data": {
            "links": {"twitter": "rochacbruno", "site": "brunorocha.org"}
        },
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data, merge=False)

    data = {"data__links__telegram": "t.me/rochacbruno"}
    toml_loader.write(
        str(tmpdir.join("settings.local.toml")), data, merge=False
    )

    settings = LazySettings(settings_file="settings.toml")
    assert settings.NAME == "Bruno"
    assert settings.COLORS == ["red", "green"]
    assert settings.DATA.links == {
        "twitter": "rochacbruno",
        "site": "brunorocha.org",
        "telegram": "t.me/rochacbruno",
    }


def test_set_new_merge_issue_241_5(tmpdir):
    data = {
        "default": {
            "name": "Bruno",
            "colors": ["red", "green"],
            "data": {
                "links": {"twitter": "rochacbruno", "site": "brunorocha.org"}
            },
        }
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data, merge=False)

    data = {"default": {"colors": "@merge ['blue']"}}
    toml_loader.write(
        str(tmpdir.join("settings.local.toml")), data, merge=False
    )

    settings = LazySettings(environments=True, settings_file="settings.toml")
    assert settings.NAME == "Bruno"
    assert settings.COLORS == ["red", "green", "blue"]
    assert settings.DATA.links == {
        "twitter": "rochacbruno",
        "site": "brunorocha.org",
    }


def test_exists(settings):
    settings.set("BOOK", "TAOCP")
    assert settings.exists("BOOK") is True


def test_dotted_traversal_access(settings):
    settings.set(
        "PARAMS",
        {
            "PASSWORD": "secret",
            "SSL": {"CONTEXT": "SECURE"},
            "DOTTED.KEY": True,
        },
        dotted_lookup=False,
    )
    assert settings.get("PARAMS") == {
        "PASSWORD": "secret",
        "SSL": {"CONTEXT": "SECURE"},
        "DOTTED.KEY": True,
    }

    assert settings("PARAMS.PASSWORD") == "secret"
    assert settings("PARAMS.SSL.CONTEXT") == "SECURE"
    assert settings("PARAMS.TOKEN.IMAGINARY", 1234) == 1234
    assert settings("IMAGINARY_KEY.FOO") is None
    assert settings("IMAGINARY_KEY") is None

    assert settings["PARAMS.PASSWORD"] == "secret"
    assert settings["PARAMS.SSL.CONTEXT"] == "SECURE"
    assert settings.PARAMS.SSL.CONTEXT == "SECURE"

    assert settings.exists("PARAMS") is True
    assert settings.exists("PARAMS.PASSWORD") is True
    assert settings.exists("PARAMS.SSL") is True
    assert settings.exists("PARAMS.SSL.FAKE") is False
    assert settings.exists("PARAMS.SSL.CONTEXT") is True

    # Dotted traversal should not work for dictionary-like key access.
    with pytest.raises(KeyError):
        settings["PARAMS.DOESNOTEXIST"]

    # Disable dot-traversal on a per-call basis.
    assert settings("PARAMS.PASSWORD", dotted_lookup=False) is None

    assert settings("PARAMS.DOTTED.KEY") is None
    assert settings("PARAMS").get("DOTTED.KEY") is True

    settings.set("DOTTED.KEY", True, dotted_lookup=False)
    assert settings("DOTTED.KEY", dotted_lookup=False) is True

    settings.set("NESTED_1", {"nested_2": {"nested_3": {"nested_4": True}}})

    assert settings.NESTED_1.nested_2.nested_3.nested_4 is True
    assert settings["NESTED_1.nested_2.nested_3.nested_4"] is True
    assert settings("NESTED_1.nested_2.nested_3.nested_4") is True
    # First key is always transformed to upper()
    assert settings("nested_1.nested_2.nested_3.nested_4") is True

    # using cast
    settings.set("me.name", '@json ["bruno", "rocha"]')
    settings.set("me.number", "42")
    assert settings.get("me.name", cast=True, default=["bruno", "rocha"]) == [
        "bruno",
        "rocha",
    ]
    assert settings.get("me.number", cast="@int", default=42) == 42

    # nested separator test
    assert settings.get("ME__NUMBER") == "42"


def test_dotted_set(settings):
    settings.set("MERGE_ENABLED_FOR_DYNACONF", False)

    settings.set("nested_1.nested_2.nested_3.nested_4", "secret")

    assert settings.NESTED_1.NESTED_2.NESTED_3.NESTED_4 == "secret"
    assert settings.NESTED_1.NESTED_2.NESTED_3.to_dict() == {
        "nested_4": "secret"
    }
    assert settings.NESTED_1.NESTED_2.to_dict() == {
        "nested_3": {"nested_4": "secret"}
    }

    assert settings.get("nested_1").to_dict() == {
        "nested_2": {"nested_3": {"nested_4": "secret"}}
    }

    with pytest.raises(KeyError):
        settings.NESTED_1.NESTED_2_0

    settings.set("nested_1.nested_2_0", "Hello")
    assert settings.NESTED_1.NESTED_2_0 == "Hello"

    settings.set("nested_1.nested_2.nested_3.nested_4", "Updated Secret")
    assert settings.NESTED_1.NESTED_2.NESTED_3.NESTED_4 == "Updated Secret"
    assert settings.NESTED_1.NESTED_2.NESTED_3.to_dict() == {
        "nested_4": "Updated Secret"
    }
    assert settings.NESTED_1.NESTED_2.to_dict() == {
        "nested_3": {"nested_4": "Updated Secret"}
    }

    assert settings.get("nested_1").to_dict() == {
        "nested_2": {"nested_3": {"nested_4": "Updated Secret"}},
        "nested_2_0": "Hello",
    }


def test_dotted_set_with_merge(settings):
    settings.set("MERGE_ENABLED_FOR_DYNACONF", False)

    start_data = {
        "default": {
            "NAME": "testdb",
            "ENGINE": "db.foo.bar",
            "PORT": 6666,
            "PARAMS": ["a", "b", "c"],
            "ATTRS": {"a": 1, "b": 2},
        }
    }
    settings.set("DATABASES", start_data)

    assert settings.DATABASES == start_data

    # Change DB name
    settings.set("DATABASES.default.NAME", "bladb")
    assert settings.DATABASES != start_data
    assert settings.DATABASES["default"].keys() == start_data["default"].keys()
    settings.DATABASES.default.NAME == "bladb"

    # Replace items on a list
    assert settings.DATABASES.default.PARAMS == ["a", "b", "c"]
    settings.set("DATABASES.default.PARAMS", ["d", "e"])
    assert settings.DATABASES != start_data
    assert settings.DATABASES["default"].keys() == start_data["default"].keys()
    assert settings.DATABASES.default.PARAMS == ["d", "e"]

    # Add new items to the list
    settings.set("DATABASES.default.PARAMS", '@merge ["e", "f", "g"]')
    assert settings.DATABASES != start_data
    assert settings.DATABASES["default"].keys() == start_data["default"].keys()
    assert settings.DATABASES.default.PARAMS == ["d", "e", "e", "f", "g"]

    # Replace a dict
    assert settings.DATABASES.default.ATTRS == {"a": 1, "b": 2}
    settings.set("DATABASES.default.ATTRS", {"c": 3})
    assert settings.DATABASES != start_data
    assert settings.DATABASES["default"].keys() == start_data["default"].keys()
    assert settings.DATABASES.default.ATTRS == {"c": 3}

    # Add new item to the dict
    settings.set("DATABASES.default.ATTRS", '@merge {"b": 2, "d": 4}')
    assert settings.DATABASES != start_data
    assert settings.DATABASES["default"].keys() == start_data["default"].keys()
    assert settings.DATABASES.default.ATTRS == {"b": 2, "c": 3, "d": 4}

    # Replace the entire list
    settings.set("DATABASES.default.PARAMS", ["x", "y", "z"], tomlfy=True)
    assert settings.DATABASES != start_data
    assert settings.DATABASES["default"].keys() == start_data["default"].keys()
    assert settings.DATABASES.default.PARAMS == ["x", "y", "z"]

    # Replace the entire dict
    settings.set("DATABASES.default.ATTRS", "{x=26}", tomlfy=True)
    assert settings.DATABASES != start_data
    assert settings.DATABASES["default"].keys() == start_data["default"].keys()
    assert settings.DATABASES.default.ATTRS == {"x": 26}


def test_from_env_method(clean_env, tmpdir):
    data = {
        "default": {"a_default": "From default env"},
        "development": {
            "value": "From development env",
            "only_in_development": True,
        },
        "other": {"value": "From other env", "only_in_other": True},
    }
    toml_path = str(tmpdir.join("base_settings.toml"))
    toml_loader.write(toml_path, data, merge=False)
    settings = LazySettings(settings_file=toml_path, environments=True)
    settings.set("ARBITRARY_KEY", "arbitrary value")

    assert settings.VALUE == "From development env"
    assert settings.A_DEFAULT == "From default env"
    assert settings.ONLY_IN_DEVELOPMENT is True
    assert settings.ARBITRARY_KEY == "arbitrary value"
    assert settings.get("ONLY_IN_OTHER") is None

    # clone the settings object pointing to a new env
    other_settings = settings.from_env("other")
    assert other_settings.VALUE == "From other env"
    assert other_settings.A_DEFAULT == "From default env"
    assert other_settings.ONLY_IN_OTHER is True
    assert other_settings.get("ARBITRARY_KEY") is None
    assert other_settings.get("ONLY_IN_DEVELOPMENT") is None
    with pytest.raises(AttributeError):
        # values set programmatically are not cloned
        other_settings.ARBITRARY_KEY
    with pytest.raises(AttributeError):
        # values set only in a specific env not cloned
        other_settings.ONLY_IN_DEVELOPMENT
    # assert it is cached not created twice
    assert other_settings is settings.from_env("other")

    # Now the same using keep=True
    other_settings = settings.from_env("other", keep=True)
    assert other_settings.VALUE == "From other env"
    assert other_settings.A_DEFAULT == "From default env"
    assert other_settings.ONLY_IN_OTHER is True
    assert other_settings.ONLY_IN_DEVELOPMENT is True
    assert settings.ARBITRARY_KEY == "arbitrary value"

    # assert it is created not cached
    assert other_settings is not settings.from_env("other")

    # settings remains the same
    assert settings.VALUE == "From development env"
    assert settings.A_DEFAULT == "From default env"
    assert settings.ONLY_IN_DEVELOPMENT is True
    assert settings.ARBITRARY_KEY == "arbitrary value"
    assert settings.get("ONLY_IN_OTHER") is None

    # additional kwargs
    data = {
        "default": {"a_default": "From default env"},
        "production": {"value": "From prod env", "only_in_prod": True},
        "other": {"value": "From other env", "only_in_other": True},
    }
    toml_path = str(tmpdir.join("other_settings.toml"))
    toml_loader.write(toml_path, data, merge=False)

    new_other_settings = other_settings.from_env(
        "production", keep=True, SETTINGS_FILE_FOR_DYNACONF=toml_path
    )

    # production values
    assert new_other_settings.VALUE == "From prod env"
    assert new_other_settings.ONLY_IN_PROD is True
    # keep=True values
    assert new_other_settings.ONLY_IN_OTHER is True
    assert new_other_settings.ONLY_IN_DEVELOPMENT is True
    assert settings.A_DEFAULT == "From default env"


def test_from_env_method_with_prefix(clean_env, tmpdir):
    data = {
        "default": {"prefix_a_default": "From default env"},
        "development": {
            "prefix_value": "From development env",
            "prefix_only_in_development": True,
        },
        "other": {
            "prefix_value": "From other env",
            "prefix_only_in_other": True,
            "not_prefixed": "no prefix",
        },
    }
    toml_path = str(tmpdir.join("base_settings.toml"))
    toml_loader.write(toml_path, data, merge=False)
    settings = LazySettings(
        settings_file=toml_path,
        environments=True,
        filter_strategy=PrefixFilter("prefix"),
    )
    settings.set("ARBITRARY_KEY", "arbitrary value")

    assert settings.VALUE == "From development env"
    assert settings.A_DEFAULT == "From default env"
    assert settings.ONLY_IN_DEVELOPMENT is True
    assert settings.ARBITRARY_KEY == "arbitrary value"
    assert settings.get("ONLY_IN_OTHER") is None

    # clone the settings object pointing to a new env
    other_settings = settings.from_env("other")
    assert other_settings.VALUE == "From other env"
    assert other_settings.A_DEFAULT == "From default env"
    assert other_settings.ONLY_IN_OTHER is True
    assert other_settings.get("ARBITRARY_KEY") is None
    assert other_settings.get("ONLY_IN_DEVELOPMENT") is None
    with pytest.raises(AttributeError):
        other_settings.not_prefixed
    with pytest.raises(AttributeError):
        # values set programmatically are not cloned
        other_settings.ARBITRARY_KEY
    with pytest.raises(AttributeError):
        # values set only in a specific env not cloned
        other_settings.ONLY_IN_DEVELOPMENT
    # assert it is cached not created twice
    assert other_settings is settings.from_env("other")


def test_preload(tmpdir):
    data = {
        "data": {"links": {"twitter": "rochacbruno", "site": "brunorocha.org"}}
    }
    toml_loader.write(str(tmpdir.join("preload.toml")), data, merge=False)

    data = {
        "dynaconf_merge": True,
        "data": {"links": {"github": "rochacbruno.github.io"}},
    }
    toml_loader.write(
        str(tmpdir.join("main_settings.toml")), data, merge=False
    )

    data = {
        "dynaconf_merge": True,
        "data": {"links": {"mastodon": "mastodon.social/@rochacbruno"}},
    }
    toml_loader.write(str(tmpdir.join("included.toml")), data, merge=False)

    settings = LazySettings(
        PRELOAD_FOR_DYNACONF=["preload.toml"],
        SETTINGS_FILE_FOR_DYNACONF="main_settings.toml",
        INCLUDES_FOR_DYNACONF=["included.toml"],
    )

    assert settings.DATA.links == {
        "twitter": "rochacbruno",
        "site": "brunorocha.org",
        "github": "rochacbruno.github.io",
        "mastodon": "mastodon.social/@rochacbruno",
    }


def test_config_aliases(tmpdir):
    data = {
        "hello": {"name": "Bruno", "passwd": 1234},
        "awesome": {"passwd": 5678},
    }
    toml_loader.write(str(tmpdir.join("blarg.toml")), data, merge=False)

    settings = LazySettings(
        envvar_prefix="BRUCE",
        core_loaders=["TOML"],
        loaders=["dynaconf.loaders.env_loader"],
        default_env="hello",
        env_switcher="BRUCE_ENV",
        prelaod=[],
        settings_file=["blarg.toml"],
        includes=[],
        ENV="awesome",
        environments=True,
    )

    assert settings.NAME == "Bruno"
    assert settings.PASSWD == 5678

    assert settings.ENVVAR_PREFIX_FOR_DYNACONF == "BRUCE"
    assert settings.CORE_LOADERS_FOR_DYNACONF == ["TOML"]
    assert settings.LOADERS_FOR_DYNACONF == ["dynaconf.loaders.env_loader"]
    assert len(settings._loaders) == 1
    assert settings.DEFAULT_ENV_FOR_DYNACONF == "hello"
    assert settings.ENV_SWITCHER_FOR_DYNACONF == "BRUCE_ENV"
    assert settings.PRELOAD_FOR_DYNACONF == []
    assert settings.SETTINGS_FILE_FOR_DYNACONF == ["blarg.toml"]
    assert settings.INCLUDES_FOR_DYNACONF == []
    assert settings.ENV_FOR_DYNACONF == "awesome"
    assert settings.current_env == "awesome"


def test_envless_mode(tmpdir):
    data = {
        "foo": "bar",
        "hello": "world",
        "default": 1,
        "databases": {"default": {"port": 8080}},
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data)

    settings = LazySettings(
        settings_file="settings.toml"
    )  # already the default
    assert settings.FOO == "bar"
    assert settings.HELLO == "world"
    assert settings.DEFAULT == 1
    assert settings.DATABASES.default.port == 8080


def test_envless_mode_with_prefix(tmpdir):
    data = {
        "prefix_foo": "bar",
        "hello": "world",
        "prefix_default": 1,
        "prefix_databases": {"default": {"port": 8080}},
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data)

    settings = LazySettings(
        settings_file="settings.toml", filter_strategy=PrefixFilter("prefix")
    )  # already the default
    assert settings.FOO == "bar"
    with pytest.raises(AttributeError):
        settings.HELLO
    assert settings.DEFAULT == 1
    assert settings.DATABASES.default.port == 8080


def test_lowercase_read_mode(tmpdir):
    """
    Starting on 3.0.0 lowercase keys are enabled by default
    """
    data = {
        "foo": "bar",
        "hello": "world",
        "default": 1,
        "databases": {"default": {"port": 8080}},
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data)

    # settings_files misspelled.. should be `settings_file`
    settings = LazySettings(settings_files="settings.toml")

    assert settings.FOO == "bar"
    assert settings.foo == "bar"
    assert settings.HELLO == "world"
    assert settings.hello == "world"
    assert settings.DEFAULT == 1
    assert settings.default == 1
    assert settings.DATABASES.default.port == 8080
    assert settings.databases.default.port == 8080

    assert "foo" in settings
    assert "FOO" in settings

    # test __dir__
    results = dir(settings)
    assert "foo" in results
    assert "FOO" in results

    results = dir(settings.databases)
    assert "default" in results
    assert "DEFAULT" in results


def test_settings_dict_like_iteration(tmpdir):
    """Settings can be iterated just like a dict"""
    data = {
        "foo": "bar",
        "hello": "world",
        "default": 1,
        "databases": {"default": {"port": 8080}},
    }
    toml_loader.write(str(tmpdir.join("settings.toml")), data)

    # settings_files misspelled.. should be `settings_file`
    settings = LazySettings(settings_files="settings.toml")

    for key in settings:
        assert key in settings._store

    for key, value in settings.items():
        assert settings._store[key] == value


def test_prefix_is_not_str_raises():
    with pytest.raises(TypeError):
        toml_loader.load(LazySettings(filter_strategy=PrefixFilter(int)))
    with pytest.raises(TypeError):
        toml_loader.load(LazySettings(filter_strategy=PrefixFilter(True)))


def test_clone():
    # create a settings object
    settings = LazySettings(FOO="bar")
    assert settings.FOO == "bar"

    # clone it
    cloned = settings.dynaconf.clone()
    assert cloned.FOO == "bar"

    # modify the cloned settings
    cloned.FOO = "baz"
    assert cloned.FOO == "baz"

    # assert original settings is not modified
    assert settings.FOO == "bar"


def test_clone_with_module_type():
    # create a settings object
    settings = LazySettings(FOO="bar", A_MODULE=os)
    # adding a module type makes object unpickaable
    # then .clone raised an error, this was fixed by copying the dict.
    assert settings.FOO == "bar"

    # clone it
    cloned = settings.dynaconf.clone()
    assert cloned.FOO == "bar"

    # modify the cloned settings
    cloned.FOO = "baz"
    assert cloned.FOO == "baz"

    # assert original settings is not modified
    assert settings.FOO == "bar"

    assert settings.A_MODULE == cloned.A_MODULE


def test_wrap_existing_settings():
    """
    Wrap an existing settings object
    """
    settings = LazySettings(FOO="bar")
    assert settings.FOO == "bar"

    # wrap it
    wrapped = LazySettings(settings._wrapped)
    assert wrapped.FOO == "bar"

    # modify the wrapped settings
    wrapped.FOO = "baz"
    assert wrapped.FOO == "baz"

    # assert original settings is also modified as they have the same wrapped
    assert settings.FOO == "baz"


def test_wrap_existing_settings_clone():
    """
    Wrap an existing settings object
    """
    settings = LazySettings(FOO="bar")
    assert settings.FOO == "bar"

    # wrap it
    wrapped = LazySettings(settings.dynaconf.clone())
    assert wrapped.FOO == "bar"

    # modify the wrapped settings
    wrapped.FOO = "baz"
    assert wrapped.FOO == "baz"

    # assert original settings is not changes as we used a wrapped clone
    assert settings.FOO == "bar"


def test_list_entries_from_yaml_should_not_duplicate_when_merged(tmpdir):
    data = {
        "default": {
            "SOME_KEY": "value",
            "SOME_LIST": ["item_1", "item_2", "item_3"],
        },
        "other": {"SOME_KEY": "new_value", "SOME_LIST": ["item_4", "item_5"]},
    }
    yaml_loader.write(str(tmpdir.join("test_settings.yaml")), data)

    settings = Dynaconf(
        settings_files="test_settings.yaml",
        environments=True,
        merge_enabled=True,
    )

    expected_default_value = BoxList(["item_1", "item_2", "item_3"])
    expected_other_value = BoxList(
        ["item_1", "item_2", "item_3", "item_4", "item_5"]
    )

    assert settings.from_env("default").SOME_LIST == expected_default_value
    assert settings.from_env("other").SOME_LIST == expected_other_value
