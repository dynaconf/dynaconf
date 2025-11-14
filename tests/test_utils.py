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
from dynaconf import DynaconfFormatError
from dynaconf import DynaconfParseError
from dynaconf.loaders.json_loader import DynaconfEncoder
from dynaconf.utils import build_env_list
from dynaconf.utils import ensure_a_list
from dynaconf.utils import ensure_upperfied_list
from dynaconf.utils import extract_json_objects
from dynaconf.utils import isnamedtupleinstance
from dynaconf.utils import Missing
from dynaconf.utils import missing
from dynaconf.utils import object_merge
from dynaconf.utils import prepare_json
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
    res = parse_conf_data("""@json {"FOO": "bar"}""")
    assert isinstance(res, dict)
    assert "FOO" in res and "bar" in res.values()

    # Test how single quotes cases are handled.
    # When jinja uses `attr` to render a json string,
    # it may convert double quotes to single quotes.
    settings.set("value", "{'FOO': 'bar'}")
    res = parse_conf_data("@json @jinja {{ this.value }}")(settings)
    assert isinstance(res, dict)
    assert "FOO" in res and "bar" in res.values()

    res = parse_conf_data("@json @format {this.value}")(settings)
    assert isinstance(res, dict)
    assert "FOO" in res and "bar" in res.values()

    # Test jinja rendering a dict
    settings.set("value", "OPTION1")
    settings.set("OPTION1", {"bar": 1})
    settings.set("OPTION2", {"bar": 2})
    res = parse_conf_data("@jinja {{ this|attr(this.value) }}")(settings)
    assert isinstance(res, str)
    res = parse_conf_data("@json @jinja {{ this|attr(this.value) }}")(settings)
    assert isinstance(res, dict)
    assert "bar" in res and res["bar"] == 1


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
def test_tomlfy_unparsable(test_input, settings):
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

    # A string is trimmed_split
    assert ensure_a_list("ab.toml") == ["ab.toml"]
    assert ensure_a_list("ab.toml,cd.toml") == ["ab.toml", "cd.toml"]
    assert ensure_a_list("ab.toml;cd.toml") == ["ab.toml", "cd.toml"]

    # other types get wrapped in a list
    assert ensure_a_list(1) == [1]


def test_ensure_upperfied_list():
    assert ensure_upperfied_list([1, "a", "A__b"]) == [1, "A", "A__b"]


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
    assert list(extract_json_objects('{{{"x": {}}}}}')) == [{"x": {}}]


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


def test_get_converter(settings):
    """Ensure the work of @get converter"""
    settings.set("FOO", 12)
    settings.set("BAR", "@get FOO")
    assert settings.BAR == settings.FOO == 12

    settings.set("ZAZ", "@get RAZ @float 42")
    assert settings.ZAZ == 42.0

    settings.set("ZAZ", "@get RAZ 34 @float")
    assert settings.ZAZ == 34.0

    settings.set("STRINGFLOAT", "23.2")
    settings.set("ZAZ", "@get STRINGFLOAT @float")
    assert settings.ZAZ == 23.2


def test_get_converter_with_1_levels(settings):
    """Ensure the work of @get converter on nested data"""
    settings.set("NAME", "Wilsom")
    settings.set("OTHERNAME", "@get name")
    assert settings.othername == "Wilsom"


def test_get_converter_with_2_levels():
    settings = Dynaconf()
    """Ensure the work of @get converter on nested data"""
    settings.set("RESTFRAMEWORK", {"AUTHENTICATION_CLASSES": ["A", "B"]})
    assert settings.RESTFRAMEWORK

    # pulp ansible
    settings.set("MYCLASSES", "@get RESTFRAMEWORK.AUTHENTICATION_CLASSES")
    assert settings.MYCLASSES[0] == "A"


def test_get_converter_with_3_levels(settings):
    """Ensure the work of @get converter on nested data"""
    settings.set("FOO__BAR__ZAZ", 12)
    settings.set("BAR", "@get FOO.BAR.ZAZ")
    assert settings.FOO.BAR.ZAZ == 12
    assert settings.BAR == 12


def test_get_converter_error_when_converting(settings):
    """Malformed declaration errors"""
    settings.set("BLA", "@get")

    with pytest.raises(DynaconfFormatError):
        settings.BLA


def test_get_converter_error_when_not_found(settings):
    """Malformed declaration errors"""
    settings.set("BLA", "@get BATATA123")

    with pytest.raises(DynaconfParseError):
        settings.BLA


def test_get_converter_quoted_default_multiword(settings):
    """Test @get converter with quoted multi-word defaults"""
    settings.set("KEY", '@get MISSING "default value here"')
    assert settings.KEY == "default value here"


def test_get_converter_quoted_default_single(settings):
    """Test @get converter with quoted single-word defaults"""
    settings.set("KEY", '@get MISSING "default"')
    assert settings.KEY == "default"


def test_get_converter_single_quoted(settings):
    """Test @get converter with single-quoted defaults"""
    settings.set("KEY", "@get MISSING 'default value'")
    assert settings.KEY == "default value"


def test_get_converter_empty_string_default(settings):
    """Test @get converter with empty string default"""
    settings.set("KEY", '@get MISSING ""')
    assert settings.KEY == ""


def test_get_converter_default_special_chars(settings):
    """Test @get converter with special characters in default"""
    settings.set("URL", '@get MISSING "http://example.com"')
    assert settings.URL == "http://example.com"


def test_get_converter_quoted_with_cast(settings):
    """Test @get converter with quoted default and cast"""
    settings.set("NUM", '@get MISSING @int "42"')
    assert settings.NUM == 42

    settings.set("NUM2", '@get MISSING "42" @int')
    assert settings.NUM2 == 42


def test_get_converter_whitespace_variations(settings):
    """Test @get converter with extra whitespace"""
    settings.set("FOO", "42")
    settings.set("KEY", "@get  FOO  @int   42")
    assert settings.KEY == 42


def test_get_converter_unclosed_quote_error(settings):
    """Test @get converter with unclosed quote raises error"""
    settings.set("KEY", '@get MISSING "unclosed')
    with pytest.raises(DynaconfFormatError, match="Unclosed quote"):
        settings.KEY


@pytest.mark.parametrize(
    "input_expected",
    [
        ({"path": Path("foo")}, {"path": "foo"}),
        ({1: Path("foo")}, {"1": "foo"}),
        ({True: Path("foo")}, {"True": "foo"}),
        ([Path("one"), Path("two"), 1, True], ["one", "two", 1, True]),
        (1, 1),
        (True, True),
        ("test", "test"),
    ],
)
def test_prepare_json(input_expected):
    data, expected = input_expected
    assert prepare_json(data) == expected


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_converter(tmp_path):
    """Assert read_file converter works"""
    # 1. Create a temp file with FOOBAR as content
    filename = tmp_path / "SECRET_KEY"
    create_file(filename, "FOOBAR")
    # 2. Create a settings file with the read_file converter
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@read_file {filename}"
        """,
    )
    # 3. Load the settings
    settings = Dynaconf(
        settings_file=settings_file,
    )
    # 4. Assert the SECRET_KEY is the content of the file
    assert settings.SECRET_KEY == "FOOBAR"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_notfound_error(tmp_path):
    """Assert read_file converter raises error on invalid file"""
    # 1. Create a settings file with the read_file converter
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@read_file {tmp_path}/non_existent_file"
        """,
    )
    # 2. Load the settings
    with pytest.raises(FileNotFoundError):
        settings = Dynaconf(
            settings_file=settings_file,
        )
        settings.SECRET_KEY


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_notfound_error_with_default(tmp_path):
    """Assert read_file converter uses default on invalid file"""
    # 1. Create a settings file with the read_file converter
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@read_file {tmp_path}/non_existent_file DEFAULT_VALUE"
        """,
    )
    # 2. Load the settings
    settings = Dynaconf(
        settings_file=settings_file,
    )
    assert settings.SECRET_KEY == "DEFAULT_VALUE"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_syntax_error(tmp_path):
    """Assert read_file converter raises error on invalid syntax"""
    # 1. Create a settings file with the read_file converter
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        """\
        SECRET_KEY = "@read_file "
        """,
    )
    # 2. Load the settings
    with pytest.raises(DynaconfFormatError):
        settings = Dynaconf(
            settings_file=settings_file,
        )
        settings.SECRET_KEY


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_with_format(tmp_path):
    """Assert read_file converter works with format"""
    # 1. Create a temp file with FOOBAR as content
    filename = tmp_path / "SECRET_KEY"
    create_file(filename, "BATATA")
    # 2. Create a settings file with the read_file converter
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        FILENAME = "{filename}"
        SECRET_KEY = "@read_file @format {{this.FILENAME}}"
        """,
    )
    # 3. Load the settings
    settings = Dynaconf(
        settings_file=settings_file,
    )
    # 4. Assert the SECRET_KEY is the content of the file
    assert settings.SECRET_KEY == "BATATA"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_with_jinja(tmp_path):
    """Assert read_file converter works with format"""
    # 1. Create a temp file with FOOBAR as content
    filename = tmp_path / "SECRET_KEY"
    create_file(filename, "POTATO")
    # 2. Create a settings file with the read_file converter
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        FILENAME = "{filename}"
        SECRET_KEY = "@read_file @jinja {{{{this.FILENAME}}}}"
        """,
    )
    # 3. Load the settings
    settings = Dynaconf(
        settings_file=settings_file,
    )
    # 4. Assert the SECRET_KEY is the content of the file
    assert settings.SECRET_KEY == "POTATO"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_with_get(tmp_path):
    """Assert read_file converter works with format"""
    # 1. Create a temp file with FOOBAR as content
    filename = tmp_path / "SECRET_KEY"
    create_file(filename, "POMME")
    # 2. Create a settings file with the read_file converter
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_FILENAME = "{filename}"
        SECRET_KEY = "@read_file @get SECRET_FILENAME"
        """,
    )
    # 3. Load the settings
    settings = Dynaconf(
        settings_file=settings_file,
    )
    # 4. Assert the SECRET_KEY is the content of the file
    assert settings.SECRET_KEY == "POMME"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_converter_with_strip(tmp_path):
    """Assert read_file converter works"""
    # 1. Create a temp file with FOOBAR as content
    filename = tmp_path / "SECRET_KEY"
    create_file(filename, "FOOBAR \n")
    # 2. Create a settings file with the read_file converter
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@strip @read_file {filename}"
        """,
    )
    # 3. Load the settings
    settings = Dynaconf(
        settings_file=settings_file,
    )
    # 4. Assert the SECRET_KEY is the content of the file
    assert settings.SECRET_KEY == "FOOBAR"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_empty_file(tmp_path):
    """Test reading an empty file returns empty string"""
    filename = tmp_path / "empty.txt"
    filename.touch()  # Create empty file
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@read_file {filename}"
        """,
    )
    settings = Dynaconf(settings_file=settings_file)
    assert settings.SECRET_KEY == ""


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_whitespace_only(tmp_path):
    """Test reading a file with only whitespace returns the content"""
    filename = tmp_path / "whitespace.txt"
    # Create a file with newlines only
    with open(filename, "w") as f:
        f.write("\n\n")
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@read_file {filename}"
        """,
    )
    settings = Dynaconf(settings_file=settings_file)
    assert settings.SECRET_KEY == "\n\n"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_path_with_spaces_quoted(tmp_path):
    """Test reading a file with spaces in path using quotes"""
    dir_with_space = tmp_path / "path with spaces"
    dir_with_space.mkdir()
    filename = dir_with_space / "file.txt"
    create_file(filename, "SECRET")

    settings_file = tmp_path / "settings.toml"
    # Need to escape quotes for TOML
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@read_file \\"{filename}\\""
        """,
    )
    settings = Dynaconf(settings_file=settings_file)
    assert settings.SECRET_KEY == "SECRET"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_quoted_path_with_default(tmp_path):
    """Test quoted path with default value"""
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        """\
        SECRET_KEY = "@read_file \\"/nonexistent/file.txt\\" fallback"
        """,
    )
    settings = Dynaconf(settings_file=settings_file)
    assert settings.SECRET_KEY == "fallback"


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_directory_error(tmp_path):
    """Test that reading a directory raises appropriate error"""
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@read_file {tmp_path}"
        """,
    )
    with pytest.raises(DynaconfFormatError, match="not a file"):
        settings = Dynaconf(settings_file=settings_file)
        settings.SECRET_KEY


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_empty_path_error(tmp_path):
    """Test that empty path raises error"""
    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        """\
        SECRET_KEY = "@read_file \\"\\""
        """,
    )
    # Empty path should raise error even with fallback
    with pytest.raises(DynaconfFormatError, match="empty path"):
        settings = Dynaconf(settings_file=settings_file)
        settings.SECRET_KEY


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Doesn't work on windows due to backslash decoding errors",
)
def test_read_file_binary_file_error(tmp_path):
    """Test that binary file raises appropriate error"""
    # Create a binary file
    binary_file = tmp_path / "binary.dat"
    with open(binary_file, "wb") as f:
        f.write(b"\x00\x01\x02\xff\xfe\xfd")

    settings_file = tmp_path / "settings.toml"
    create_file(
        settings_file,
        f"""\
        SECRET_KEY = "@read_file {binary_file}"
        """,
    )
    with pytest.raises(DynaconfFormatError, match="not a UTF-8 text file"):
        settings = Dynaconf(settings_file=settings_file)
        settings.SECRET_KEY


def test_string_utils():
    """Test string utils"""
    assert parse_conf_data("@upper foo") == "FOO"
    assert parse_conf_data("@lower FOO") == "foo"
    assert parse_conf_data("@title foo bar") == "Foo Bar"
    assert parse_conf_data("@capitalize foo bar") == "Foo bar"
    assert parse_conf_data("@strip foo bar \n") == "foo bar"
    assert parse_conf_data("@lstrip foo bar \n") == "foo bar \n"
    assert parse_conf_data("@rstrip foo bar \n") == "foo bar"
    assert parse_conf_data("@split foo bar") == ["foo", "bar"]
    assert parse_conf_data("@casefold Foo BAR") == "foo bar"
    assert parse_conf_data("@swapcase Foo BAR") == "fOO bar"


# NEW TESTS FOR EDGE CASES


def test_insert_quoted_multiword_value(settings):
    """Test @insert with quoted multi-word values"""
    settings.set("ITEMS", [1, 2, 3])
    settings.set("ITEMS", '@insert 0 "hello world"')
    assert settings.ITEMS == ["hello world", 1, 2, 3]


def test_insert_single_quoted_value(settings):
    """Test @insert with single-quoted values"""
    settings.set("ITEMS", [1, 2])
    settings.set("ITEMS", "@insert 0 'test value'")
    assert settings.ITEMS == ["test value", 1, 2]


def test_insert_quoted_empty_string(settings):
    """Test @insert with empty string"""
    settings.set("ITEMS", [1, 2])
    settings.set("ITEMS", '@insert 0 ""')
    assert settings.ITEMS == ["", 1, 2]


def test_insert_with_json(settings):
    """Test @insert with JSON object"""
    settings.set("ITEMS", [])
    settings.set("ITEMS", '@insert 0 @json {"key": "value"}')
    assert settings.ITEMS == [{"key": "value"}]


def test_insert_negative_index(settings):
    """Test @insert with negative index"""
    settings.set("ITEMS", [1, 2, 3])
    settings.set("ITEMS", "@insert -1 99")
    assert settings.ITEMS == [1, 2, 99, 3]


def test_json_with_apostrophes(settings):
    """Test @json with apostrophes in string values"""
    settings.set("DATA", """@json {"message": "It's working"}""")
    assert settings.DATA == {"message": "It's working"}


def test_json_single_quoted_dict(settings):
    """Test @json with single-quoted Python dict"""
    settings.set("DATA", "@json {'key': 'value'}")
    assert settings.DATA == {"key": "value"}


def test_json_mixed_quotes(settings):
    """Test @json with mixed quotes"""
    settings.set("DATA", """@json {'outer': "inner"}""")
    assert settings.DATA == {"outer": "inner"}


def test_json_nested_quotes(settings):
    """Test @json with nested quotes"""
    settings.set("DATA", """@json {"key": "value with 'quotes'"}""")
    assert settings.DATA == {"key": "value with 'quotes'"}


def test_bool_with_whitespace(settings):
    """Test @bool with whitespace"""
    settings.set("FLAG", "@bool   true  ")
    assert settings.FLAG is True

    settings.set("FLAG2", "@bool  false  ")
    assert settings.FLAG2 is False


def test_bool_whitespace_empty_string(settings):
    """Test @bool with whitespace-only string (empty after strip)"""
    # Note: empty string after strip is in false_values
    settings.set("FLAG", "@bool    ")
    assert settings.FLAG is False


def test_merge_quoted_value_with_comma(settings):
    """Test @merge with quoted values containing commas"""
    settings.set("CONFIG", """@merge message="Hello, World!" count=5""")
    assert settings.CONFIG.message == "Hello, World!"
    assert settings.CONFIG.count == 5


def test_merge_quoted_value_with_equals(settings):
    """Test @merge with quoted values containing equals"""
    settings.set("CONFIG", """@merge url="http://api.com?key=value" """)
    assert settings.CONFIG.url == "http://api.com?key=value"


def test_merge_empty_value(settings):
    """Test @merge with empty value"""
    settings.set("CONFIG", '@merge key=""')
    assert settings.CONFIG.key == ""


def test_merge_spaces_around_equals(settings):
    """Test @merge with spaces around equals"""
    settings.set("CONFIG", "@merge key = value")
    assert settings.CONFIG.key == "value"


def test_merge_duplicate_keys(settings):
    """Test @merge with duplicate keys (last one wins)"""
    settings.set("CONFIG", "@merge key=first key=second")
    # Should have only one key, with the last value
    assert settings.CONFIG.key == "second"


def test_int_converter_error_handling(settings):
    """Test @int with invalid input raises DynaconfParseError"""
    with pytest.raises(DynaconfParseError, match="Cannot convert"):
        settings.set("NUM", "@int abc")


def test_float_converter_error_handling(settings):
    """Test @float with invalid input raises DynaconfParseError"""
    with pytest.raises(DynaconfParseError, match="Cannot convert"):
        settings.set("NUM", "@float xyz")


def test_format_circular_reference(settings):
    """Test circular reference detection in @format"""
    settings.set("A", "@format {this.B}")
    settings.set("B", "@format {this.A}")

    with pytest.raises(DynaconfFormatError, match="Circular reference"):
        settings.A


def test_string_utils_with_numbers(settings):
    """Test string utilities with numeric input"""
    settings.set("NUM", "@upper 42")
    assert settings.NUM == "42"


def test_string_utils_with_none(settings):
    """Test string utilities with None"""
    settings.set("VAL", "@title None")
    assert settings.VAL == "None"


def test_read_file_with_get_combo(tmp_path, settings):
    """Test @read_file combined with @get"""
    filename = tmp_path / "secret.txt"
    create_file(filename, "SECRET_VALUE")

    settings.set("FILENAME", str(filename))
    settings.set("SECRET", "@read_file @get FILENAME")
    assert settings.SECRET == "SECRET_VALUE"


def test_int_with_get_combo(settings):
    """Test @int combined with @get"""
    settings.set("NUMBER_STR", "42")
    settings.set("NUMBER", "@int @get NUMBER_STR")
    assert settings.NUMBER == 42
