from __future__ import annotations

from collections import namedtuple

import pytest
from flask import Flask

from dynaconf.contrib import FlaskDynaconf
from tests_functional.flask_with_dotenv.app import app as flask_app


DBDATA = namedtuple("DbData", ["server", "port"])


def test_named_tuple_config():
    app = Flask(__name__)
    app.config["DBDATA"] = DBDATA(server="localhost", port=5432)
    FlaskDynaconf(app)
    assert app.config["DBDATA"].server == "localhost"
    assert app.config["DBDATA"].port == 5432
    assert isinstance(app.config["DBDATA"], DBDATA)


def test_named_tuple_config_using_initapp():
    app = Flask(__name__)
    FlaskDynaconf(app)
    app.config["DBDATA"] = DBDATA(server="localhost", port=5432)
    assert app.config["DBDATA"].server == "localhost"
    assert app.config["DBDATA"].port == 5432
    assert isinstance(app.config["DBDATA"], DBDATA)


def test_dynamic_load_exts(settings):
    """Assert that a config based extensions are loaded"""
    app = Flask(__name__)
    app.config["EXTENSIONS"] = [
        "tests_functional.dummy_flask_extension.dummy:init_app"
    ]
    FlaskDynaconf(app, dynaconf_instance=settings)
    app.config.load_extensions()
    assert app.config.EXTENSIONS == [
        "tests_functional.dummy_flask_extension.dummy:init_app"
    ]
    assert app.is_dummy_loaded is True


def test_dynamic_load_entry_point(settings):
    """Assert that a config based extensions support entry point syntax"""
    app = Flask(__name__)
    app.config["EXTENSIONS"] = [
        "tests_functional.dummy_flask_extension:dummy_instance.init_app"
    ]
    FlaskDynaconf(app, dynaconf_instance=settings)
    app.config.load_extensions()
    assert app.config.EXTENSIONS == [
        "tests_functional.dummy_flask_extension:dummy_instance.init_app"
    ]
    assert app.extensions["dummy"].__class__.__name__ == "DummyExtensionType"


def test_dynamic_load_exts_list(settings):
    """Assert that a config based extensions are loaded"""
    app = Flask(__name__)
    app.config["EXTENSIONS"] = [
        "tests_functional.dummy_flask_extension.dummy:init_app"
    ]
    FlaskDynaconf(app, dynaconf_instance=settings, extensions_list=True)
    assert app.config.EXTENSIONS == [
        "tests_functional.dummy_flask_extension.dummy:init_app"
    ]
    assert app.is_dummy_loaded is True


def test_dynamic_load_exts_no_list(settings):
    """Assert that a config based extensions are loaded"""
    app = Flask(__name__)
    FlaskDynaconf(app, dynaconf_instance=settings, extensions_list=True)


def test_flask_dynaconf(settings):
    """
    Test Flask app wrapped with FlaskDynaconf
    """
    app = Flask(__name__)
    app.config["MY_VAR"] = "foo"
    FlaskDynaconf(app, dynaconf_instance=settings)
    app.config["MY_VAR2"] = "bar"

    assert app.config.HOSTNAME == "host.com"
    assert app.config.MY_VAR == "foo"

    assert app.config["HOSTNAME"] == "host.com"
    assert app.config["MY_VAR"] == "foo"

    assert app.config.get("HOSTNAME") == "host.com"
    assert app.config.get("MY_VAR") == "foo"

    assert app.config("HOSTNAME") == "host.com"
    assert app.config("MY_VAR") == "foo"

    assert "HOSTNAME" in app.config
    assert "MY_VAR" in app.config

    # ref: #521
    assert "NONEXISTENETVAR" not in app.config
    assert ("NONEXISTENETVAR" in app.config) is False

    assert "MY_VAR" in app.config
    assert "MY_VAR2" in app.config
    assert "MY_VAR" in app.config.keys()
    assert "MY_VAR2" in app.config.keys()
    assert ("MY_VAR", "foo") in app.config.items()
    assert ("MY_VAR2", "bar") in app.config.items()
    assert "foo" in app.config.values()
    assert "bar" in app.config.values()
    assert "MY_VAR" in list(app.config)
    assert "MY_VAR2" in list(app.config)
    assert app.config.setdefault("MY_VAR", "default") == "foo"
    assert app.config.setdefault("MY_VAR2", "default") == "bar"
    assert app.config.setdefault("DEFAULT_VAR", "default") == "default"
    assert app.config["DEFAULT_VAR"] == "default"

    with pytest.raises(KeyError):
        app.config["NONEXISTENETVAR"]

    with pytest.raises(AttributeError):
        app.config.nonexistentattribute


def test_flask_with_dot_env():
    envvars = {
        "HELLO": "hello flask",
        "INTVAR": 42,
        "FLOATVAR": 4.2,
        "BOOLVAR": True,
        "JSONVAR": ["flask", "rocks"],
    }
    for key, value in envvars.items():
        assert flask_app.config[key] == value


def test_flask_dotenv_cli():
    with flask_app.test_client() as client:
        assert client.get("/test").data == b"hello flask"
