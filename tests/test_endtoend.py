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
