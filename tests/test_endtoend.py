from __future__ import annotations

import os


def test_end_to_end(settings):
    """
    settings is fixture configured in conftest.py
    """
    assert settings.HOSTNAME == "host.com"

    assert settings.PORT == 5000
    assert isinstance(settings.PORT, int)

    assert settings.VALUE == 42.1
    assert isinstance(settings.VALUE, float)

    assert settings.DEBUG is True
    assert isinstance(settings.DEBUG, bool)

    assert settings.ALIST == ["item1", "item2", "item3"]
    assert isinstance(settings.ALIST, list)
    assert len(settings.ALIST) == 3

    assert settings.ADICT == {"key": "value"}
    assert isinstance(settings.ADICT, dict)
    assert "key" in settings.ADICT

    assert settings.get("FOO", default="bar") == "bar"

    assert settings.HOSTNAME == "host.com"

    if settings.exists_in_environ("TRAVIS"):
        assert settings.ENV_BOOLEAN is True
        assert settings.ENV_INT == 42
        assert settings.ENV_FLOAT == 42.2
        assert settings.ENV_LIST == ["dyna", "conf"]
        assert settings.ENV_PURE_INT == 42
        assert settings.ENV_STR_INT == "42"
        assert settings.as_int("ENV_PURE_INT") == 42
        assert settings.get("ENV_PURE_INT", cast="@int") == 42
        assert isinstance(settings.ENV_DICT, dict)

        os.environ["ENVVAR_PREFIX_FOR_DYNACONF"] = "OTHER"
        with settings.using_env("OTHER"):
            assert settings.TESTING is True
            assert settings.ENABLED is True
            assert settings.DISABLED is False
        os.environ["ENVVAR_PREFIX_FOR_DYNACONF"] = "DYNACONF"


def test_boxed_data(settings):
    assert settings.BOXED_DATA.host == "server.com"
    assert settings.BOXED_DATA.port == 8080
    assert settings.BOXED_DATA.params.username == "admin"
    assert settings.BOXED_DATA.params.password == "secret"
    assert settings.BOXED_DATA.params.token.type == 1
    assert settings.BOXED_DATA.params.token.value == 2


def test_boxed_data_call(settings):
    assert settings("boxed_data").host == "server.com"
    assert settings("boxed_data").port == 8080
    assert settings("boxed_data").params.username == "admin"
    assert settings("boxed_data").params.password == "secret"
    assert settings("boxed_data").params.token.type == 1
    assert settings("boxed_data").params.token.value == 2


def test_359_jinja_interpolation():
    from dynaconf import Dynaconf

    data = {
        "template": "hello",
        "a": {
            "main": "@jinja {{this.template}} world",
        },
    }
    settings = Dynaconf(**data)

    expected = {"main": "hello world"}
    assert settings.get("a.main") == "hello world"
    assert settings.get("a").to_dict() == expected


def test_392_interpolation_inside_list():
    from dynaconf import Dynaconf

    data = {
        "myvalue": "hello",
        "a": {
            "listy": ["@format {this.myvalue} world"],
        },
    }
    settings = Dynaconf(**data)

    assert settings.a.listy[0] == "hello world"
    assert settings.a.listy == ["hello world"]


class TestIssue905:
    def test_setdefault_has_no_side_effect(self):
        from dynaconf import Dynaconf
        from dynaconf import Validator

        data = {
            "a": {
                "listy": ["1", "2"],
            },
        }
        settings = Dynaconf(**data, merge_enabled=True)
        validator_with_default = Validator("a.something_new", default=5)
        settings.validators.register(validator_with_default)
        settings.validators.validate()
        assert settings.a.listy == ["1", "2"]

    def test_envvar_double_quotes_casting(self, settings):
        # LISTY_STRING_INT{i} are defined in the tests/.env
        # The 905 bug is about a side-effect of validator default. Doing setdefault
        # to a.b would affect a.c. In that scenario, were testing that "'1'" was casted
        # o "1", but that was a side-effect by itself. Now the side-effect nature of
        # the bug was fixed with tomlfy_filter, so we shouldnt' have this cast anymore.
        assert settings.LISTY_STRING_INT1 == ["'1'", "'2'"]
        assert settings.LISTY_STRING_INT2 == ["1", "2"]
