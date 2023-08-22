from __future__ import annotations

import json
import os
import sys
from collections import namedtuple
from pathlib import Path
from textwrap import dedent

import pytest

from dynaconf import add_converter
from dynaconf import default_settings
from dynaconf import Dynaconf
from dynaconf.loaders.json_loader import DynaconfEncoder
from dynaconf.utils import build_env_list
from dynaconf.utils import ensure_a_list
from dynaconf.utils import extract_json_objects
from dynaconf.utils import isnamedtupleinstance
from dynaconf.utils import Missing
from dynaconf.utils import missing
from dynaconf.utils import object_merge
from dynaconf.utils import trimmed_split
from dynaconf.utils import upperfy
from dynaconf.utils.files import find_file
from dynaconf.utils.files import get_local_filename
from dynaconf.utils.parse_conf import boolean_fix
from dynaconf.utils.parse_conf import evaluate_lazy_format
from dynaconf.utils.parse_conf import Formatters
from dynaconf.utils.parse_conf import Lazy
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.utils.parse_conf import try_to_encode
from dynaconf.utils.parse_conf import unparse_conf_data


def test_isnamedtupleinstance():
    """Assert that isnamedtupleinstance works as expected"""
    Db = namedtuple("Db", ["host", "port"])
    assert isnamedtupleinstance(Db(host="localhost", port=3306))
    assert not isnamedtupleinstance(dict(host="localhost", port=3306.0))
    assert not isnamedtupleinstance(("localhost", "3306"))

    class Foo(tuple):
        def _fields(self):
            return ["a", "b"]

    assert not isnamedtupleinstance(Foo())


def test_unparse():
    """Assert bare types are reversed cast"""
    assert unparse_conf_data("teste") == "teste"
    assert unparse_conf_data(123) == "@int 123"
    assert unparse_conf_data(123.4) == "@float 123.4"
    assert unparse_conf_data(False) == "@bool False"
    assert unparse_conf_data(True) == "@bool True"
    assert unparse_conf_data(["a", "b"]) == '@json ["a", "b"]'
    assert unparse_conf_data({"name": "Bruno"}) == '@json {"name": "Bruno"}'
    assert unparse_conf_data(None) == "@none "
    assert unparse_conf_data(Lazy("{foo}")) == "@format {foo}"


def test_cast_bool(settings):
    """Covers https://github.com/dynaconf/dynaconf/issues/14"""
    assert parse_conf_data(False, box_settings=settings) is False
    assert settings.get("SIMPLE_BOOL", cast="@bool") is False


def test_find_file(tmpdir):
    """
    Create a temporary folder structure like the following:
        tmpXiWxa5/
        └── child1
            └── child2
                └── child3
                    └── child4
                       └── .env
                       └── app.py

    1) Then try to automatically `find_dotenv` starting in `child4`
    """

    curr_dir = tmpdir
    dirs = []
    for f in ["child1", "child2", "child3", "child4"]:
        curr_dir = os.path.join(str(curr_dir), f)
        dirs.append(curr_dir)
        os.mkdir(curr_dir)

    child4 = dirs[-1]

    assert find_file("file-does-not-exist") == ""
    assert find_file("/abs-file-does-not-exist") == ""

    for _dir in dirs:
        # search for abspath return the same path
        assert os.path.isabs(_dir)
        assert find_file(_dir) == _dir

    # now place a .env file a few levels up and make sure it's found
    filename = os.path.join(str(child4), ".env")
    with open(
        filename, "w", encoding=default_settings.ENCODING_FOR_DYNACONF
    ) as f:
        f.write("TEST=test\n")

    assert find_file(project_root=str(child4)) == filename

    # skip the inner child4/.env and force the find of /tmp.../.env
    assert find_file(
        project_root=str(child4), skip_files=[filename]
    ) == os.path.join(str(tmpdir), ".env")


def test_casting_str(settings):
    res = parse_conf_data("@str 7")
    assert isinstance(res, str) and res == "7"

    settings.set("value", 7)
    res = parse_conf_data("@str @jinja {{ this.value }}")(settings)
    assert isinstance(res, str) and res == "7"

    res = parse_conf_data("@str @format {this.value}")(settings)
    assert isinstance(res, str) and res == "7"


def test_casting_int(settings):
    res = parse_conf_data("@int 2")
    assert isinstance(res, int) and res == 2

    settings.set("value", 2)
    res = parse_conf_data("@int @jinja {{ this.value }}")(settings)
    assert isinstance(res, int) and res == 2

    res = parse_conf_data("@int @format {this.value}")(settings)
    assert isinstance(res, int) and res == 2


def test_casting_float(settings):
    res = parse_conf_data("@float 0.3")
    assert isinstance(res, float) and abs(res - 0.3) < 1e-6

    settings.set("value", 0.3)
    res = parse_conf_data("@float @jinja {{ this.value }}")(settings)
    assert isinstance(res, float) and abs(res - 0.3) < 1e-6

    res = parse_conf_data("@float @format {this.value}")(settings)
    assert isinstance(res, float) and abs(res - 0.3) < 1e-6


def test_casting_bool(settings):
    res = parse_conf_data("@bool true")
    assert isinstance(res, bool) and res is True

    settings.set("value", "true")
    res = parse_conf_data("@bool @jinja {{ this.value }}")(settings)
    assert isinstance(res, bool) and res is True

    settings.set("value", "false")
    res = parse_conf_data("@bool @format {this.value}")(settings)
    assert isinstance(res, bool) and res is False


def test_casting_json(settings):
    # Testing cases where input is strictly json
    res = parse_conf_data(
        """@json {
            "FOO": "bar",
            "key": false,
            "somekey": "this is a 'value' with single quote"
        }"""
    )
    assert isinstance(res, dict)
    assert "FOO" in res and "bar" in res.values()
    # parsing true and false okay
    assert "key" in res and False in res.values()
    # parsing single quote okay
    assert "somekey" in res and "'value'" in res["somekey"]

    # Testing invalid json: single quotes
    json_err = json.decoder.JSONDecodeError
    err_str = "Expecting property name enclosed in double quotes"
    with pytest.raises(json_err, match=err_str):
        res = parse_conf_data("""@json {'FOO': 'bar'}""")

    # Testing invalid json: upper case True
    with pytest.raises(json_err, match="Expecting value"):
        res = parse_conf_data("""@json {"FOO": True}""")

    # Testing jinja parsed dictionary
    settings.set("value", {"FOO": "bar", "Y": True, "Z": "False"})
    # This will fail since jinja will convert the
    # dict to string using single quotes
    with pytest.raises(json_err, match=err_str):
        res = parse_conf_data("@json @jinja {{ this.value }}")(settings)
    # However, casting to json first before parsing will pass
    res = parse_conf_data("@json @jinja {{ this.value | tojson }}")(settings)
    assert isinstance(res, dict)
    assert "FOO" in res and "bar" == res["FOO"]
    assert "Y" in res and res["Y"] is True
    assert "Z" in res and res["Z"] == "False"

    # Testing format parsed dictionary
    # This will fail if 'value' is a dict
    with pytest.raises(json_err, match=err_str):
        res = parse_conf_data("@json @format {this.value}")(settings)
    # This will work if 'value' is a proper json string
    settings.set("value", '{"FOO": "bar", "Y": true, "Z": "False"}')
    parse_conf_data("@json @format {this.value}")(settings)
    assert isinstance(res, dict)
    assert "FOO" in res and "bar" == res["FOO"]
    assert "Y" in res and res["Y"] is True
    assert "Z" in res and res["Z"] == "False"

    # Test jinja rendering a dict
    settings.set("value", "OPTION1")
    settings.set("OPTION1", {"bar": 1})
    settings.set("OPTION2", {"bar": 2})
    res = parse_conf_data("@jinja {{ this|attr(this.value) }}")(settings)
    assert isinstance(res, str)
    with pytest.raises(json_err, match=err_str):
        res = parse_conf_data("@json @jinja {{ this|attr(this.value) }}")(
            settings
        )
    res = parse_conf_data("@json @jinja {{ this|attr(this.value)|tojson }}")(
        settings
    )
    assert isinstance(res, dict)
    assert "bar" in res and res["bar"] == 1


def test_casting_pyliteral(settings):
    # Testing cases where the input is strictly json
    # This will fail at the boolean
    with pytest.raises(ValueError):
        res = parse_conf_data(
            """@py_literal {
                "FOO": "bar",
                "key": false,
                "somekey": "this is a 'value' with single quote"
            }"""
        )

    # Testing cases where input is a dict but not
    # strictly json
    res = parse_conf_data(
        """@py_literal {
            "FOO": "bar",
            "key": False,
            'somekey': "this is a 'value' with single quote"
        }"""
    )
    assert isinstance(res, dict)
    assert "FOO" in res and res["FOO"] == "bar"
    assert "key" in res and res["key"] is False
    assert "somekey" in res and "'value'" in res["somekey"]

    # Testing list
    res = parse_conf_data("""@py_literal ["a", "b", 'c', 1]""")
    assert isinstance(res, list)


def test_disable_cast(monkeypatch):
    # this casts for int
    assert parse_conf_data("@int 42", box_settings={}) == 42
    # now gives pure string
    with monkeypatch.context() as m:
        m.setenv("AUTO_CAST_FOR_DYNACONF", "off")
        assert parse_conf_data("@int 42", box_settings={}) == "@int 42"


def test_disable_cast_on_instance():
    settings = Dynaconf(auto_cast=False, environments=True)
    assert settings.auto_cast_for_dynaconf is False
    settings.set("SIMPLE_INT", "@int 42")
    assert settings.get("SIMPLE_INT") == "@int 42"


def test_tomlfy(settings):
    assert parse_conf_data("1", tomlfy=True, box_settings=settings) == 1
    assert parse_conf_data("true", tomlfy=True, box_settings=settings) is True
    assert (
        parse_conf_data("'true'", tomlfy=True, box_settings=settings) == "true"
    )
    assert parse_conf_data('"42"', tomlfy=True, box_settings=settings) == "42"
    assert parse_conf_data(
        "[1, 32, 3]", tomlfy=True, box_settings=settings
    ) == [1, 32, 3]
    assert parse_conf_data(
        "[1.1, 32.1, 3.3]", tomlfy=True, box_settings=settings
    ) == [1.1, 32.1, 3.3]
    assert parse_conf_data(
        "['a', 'b', 'c']", tomlfy=True, box_settings=settings
    ) == ["a", "b", "c"]
    assert parse_conf_data(
        "[true, false]", tomlfy=True, box_settings=settings
    ) == [True, False]
    assert parse_conf_data(
        "{key='value', v=1}", tomlfy=True, box_settings=settings
    ) == {"key": "value", "v": 1}


@pytest.mark.parametrize("test_input", ["something=42"])
def test_tomlfy_unparseable(test_input, settings):
    assert (
        parse_conf_data(test_input, tomlfy=True, box_settings=settings)
        == test_input
    )


def test_missing_sentinel():

    # The missing singleton should always compare truthfully to itself
    assert missing == missing

    # new instances of Missing should be equal to each other due to
    # explicit __eq__ implementation check for isinstance.
    assert missing == Missing()

    # The sentinel should not be equal to None, True, or False
    assert missing is not None
    assert missing is not True
    assert missing is not False

    # But the explicit typecasting of missing to a bool should evaluate to
    # False
    assert bool(missing) is False

    assert str(missing) == "<dynaconf.missing>"


def test_meta_values(settings):
    reset = parse_conf_data(
        "@reset [1, 2]", tomlfy=True, box_settings=settings
    )
    assert reset.value == [1, 2]
    assert reset._dynaconf_reset is True
    assert "Reset([1, 2])" in repr(reset)

    _del = parse_conf_data("@del", tomlfy=True, box_settings=settings)
    assert _del.value == ""
    assert _del._dynaconf_del is True
    assert "Del()" in repr(_del)


def test_merge_existing_list():
    existing = ["bruno", "karla"]
    object_merge(existing, existing)
    # calling twice the same object does not duplicate
    assert existing == ["bruno", "karla"]

    new = ["erik", "bruno"]
    object_merge(existing, new)
    assert new == ["bruno", "karla", "erik", "bruno"]


def test_merge_existing_list_unique():
    existing = ["bruno", "karla"]
    new = ["erik", "bruno"]
    object_merge(existing, new, unique=True)
    assert new == ["karla", "erik", "bruno"]


def test_merge_existing_dict():
    existing = {"host": "localhost", "port": 666}
    new = {"user": "admin"}

    # calling with same data has no effect
    object_merge(existing, existing)
    assert existing == {"host": "localhost", "port": 666}

    object_merge(existing, new)
    assert new == {"host": "localhost", "port": 666, "user": "admin"}


def test_merge_dict_with_meta_values(settings):
    existing = {"A": 1, "B": 2, "C": 3}
    new = {
        "B": parse_conf_data("@del", tomlfy=True, box_settings=settings),
        "C": parse_conf_data("4", tomlfy=True, box_settings=settings),
    }
    object_merge(existing, new)
    assert new == {"A": 1, "C": 4}


def test_trimmed_split():
    # No sep
    assert trimmed_split("hello") == ["hello"]

    # a comma sep string
    assert trimmed_split("ab.toml,cd.yaml") == ["ab.toml", "cd.yaml"]
    # spaces are trimmed
    assert trimmed_split(" ab.toml , cd.yaml ") == ["ab.toml", "cd.yaml"]

    # a semicollon sep string
    assert trimmed_split("ab.toml;cd.yaml") == ["ab.toml", "cd.yaml"]
    # semicollon are trimmed
    assert trimmed_split(" ab.toml ; cd.yaml ") == ["ab.toml", "cd.yaml"]

    # has comma and also semicollon (semicollon has precedence)
    assert trimmed_split("ab.toml,cd.yaml;ef.ini") == [
        "ab.toml,cd.yaml",
        "ef.ini",
    ]

    # has comma and also semicollon (changing precedence)
    assert trimmed_split("ab.toml,cd.yaml;ef.ini", seps=(",", ";")) == [
        "ab.toml",
        "cd.yaml;ef.ini",
    ]

    # using different separator
    assert trimmed_split("ab.toml|cd.yaml", seps=("|")) == [
        "ab.toml",
        "cd.yaml",
    ]


def test_ensure_a_list():

    # No data is empty list
    assert ensure_a_list(None) == []

    # Sequence types is only converted
    assert ensure_a_list([1, 2]) == [1, 2]
    assert ensure_a_list((1, 2)) == [1, 2]
    assert ensure_a_list({1, 2}) == [1, 2]

    # A string is trimmed_splitted
    assert ensure_a_list("ab.toml") == ["ab.toml"]
    assert ensure_a_list("ab.toml,cd.toml") == ["ab.toml", "cd.toml"]
    assert ensure_a_list("ab.toml;cd.toml") == ["ab.toml", "cd.toml"]

    # other types get wrapped in a list
    assert ensure_a_list(1) == [1]


def test_get_local_filename():
    settings_path = os.path.join("foo", "b", "conf.toml")
    local_path = os.path.join("foo", "b", "conf.local.toml")
    assert get_local_filename(settings_path) == local_path


def test_upperfy():
    assert upperfy("foo") == "FOO"
    assert upperfy("foo__bar") == "FOO__bar"
    assert upperfy("foo__bar__ZAZ") == "FOO__bar__ZAZ"
    assert (
        upperfy("foo__bar__ZAZ__naz__TAZ_ZAZ") == "FOO__bar__ZAZ__naz__TAZ_ZAZ"
    )
    assert upperfy("foo_bar") == "FOO_BAR"
    assert upperfy("foo_BAR") == "FOO_BAR"


def test_lazy_format_class():
    value = Lazy("{this[FOO]}/bar")
    settings = {"FOO": "foo"}
    assert value(settings) == "foo/bar"
    assert str(value) == value.value
    assert repr(value) == f"'@{value.formatter} {value.value}'"


def test_evaluate_lazy_format_decorator(settings):
    class Settings:
        FOO = "foo"
        AUTO_CAST_FOR_DYNACONF = True

        @evaluate_lazy_format
        def get(self, key, default=None):
            if key.endswith("_FOR_DYNACONF"):
                return getattr(self, key)
            return parse_conf_data("@format {this.FOO}/bar", box_settings=self)

    settings = Settings()
    assert settings.get("foo") == "foo/bar"


def test_lazy_format_on_settings(settings):
    os.environ["ENV_THING"] = "LazyFormat"
    settings.set("set_1", "really")
    settings.set("lazy", "@format {env[ENV_THING]}/{this[set_1]}/{this.SET_2}")
    settings.set("set_2", "works")

    assert settings.LAZY == settings.get("lazy") == "LazyFormat/really/works"


def test_lazy_format_class_jinja():
    value = Lazy("{{this['FOO']}}/bar", formatter=Formatters.jinja_formatter)
    settings = {"FOO": "foo"}
    assert value(settings) == "foo/bar"


def test_evaluate_lazy_format_decorator_jinja(settings):
    class Settings:
        FOO = "foo"

        AUTO_CAST_FOR_DYNACONF = True

        @evaluate_lazy_format
        def get(self, key, default=None):
            if key.endswith("_FOR_DYNACONF"):
                return getattr(self, key)
            return parse_conf_data(
                "@jinja {{this.FOO}}/bar", box_settings=settings
            )

    settings = Settings()
    assert settings.get("foo") == "foo/bar"


def test_lazy_format_on_settings_jinja(settings):
    os.environ["ENV_THING"] = "LazyFormat"
    settings.set("set_1", "really")
    settings.set(
        "lazy", "@jinja {{env.ENV_THING}}/{{this['set_1']}}/{{this.SET_2}}"
    )
    settings.set("set_2", "works")

    assert settings.LAZY == settings.get("lazy") == "LazyFormat/really/works"


def test_lazy_format_is_json_serializable():
    value = Lazy("{this[FOO]}/bar")
    assert (
        json.dumps({"val": value}, cls=DynaconfEncoder)
        == '{"val": "@format {this[FOO]}/bar"}'
    )


def test_try_to_encode():
    value = Lazy("{this[FOO]}/bar")
    assert try_to_encode(value) == "@format {this[FOO]}/bar"


def test_del_raises_on_unwrap(settings):
    value = parse_conf_data("@del ", box_settings=settings)
    with pytest.raises(ValueError):
        value.unwrap()


def test_extract_json():
    assert list(extract_json_objects("foo bar")) == []
    assert list(extract_json_objects('foo bar {"a": 1}')) == [{"a": 1}]
    assert list(extract_json_objects("foo bar {'a': 2{")) == []
    assert list(extract_json_objects('{{{"x": {}}}}')) == [{"x": {}}]


def test_env_list():
    class Obj(dict):
        @property
        def current_env(self):
            return "other"

    assert build_env_list(Obj(), env="OTHER") == [
        "default",
        "dynaconf",
        "other",
        "global",
    ]


def create_file(filename: str, data: str) -> str:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(dedent(data))
    return filename


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_add_converter_path_example(tmp_path):
    """Assert add_converter Path example works"""
    add_converter("path", Path)
    fn = create_file(
        tmp_path / "settings.yaml",
        f"""\
        my_path: "@path {Path.home()}"
        """,
    )
    settings = Dynaconf(settings_file=fn)
    assert isinstance(settings.my_path, Path)


def test_boolean_fix():
    """Assert boolean fix works"""
    assert boolean_fix("True") == "true"
    assert boolean_fix("False") == "false"
    assert boolean_fix("NotOnlyTrue") == "NotOnlyTrue"
    assert boolean_fix("TrueNotOnly") == "TrueNotOnly"
    assert boolean_fix("FalseNotOnly") == "FalseNotOnly"
    assert boolean_fix("NotOnlyFalse") == "NotOnlyFalse"
