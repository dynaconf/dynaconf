from flask import Flask

from dynaconf.contrib import FlaskDynaconf
from example.flask_with_dotenv.app import app as flask_app


def test_dynamic_load_exts(settings):
    """Assert that a config based extensions are loaded"""
    app = Flask(__name__)
    app.config["EXTENSIONS"] = ["example.dummy_flask_extension.dummy:init_app"]
    FlaskDynaconf(app, dynaconf_instance=settings)
    app.config.load_extensions()
    assert app.config.EXTENSIONS == [
        "example.dummy_flask_extension.dummy:init_app"
    ]
    assert app.is_dummy_loaded is True


def test_dynamic_load_entry_point(settings):
    """Assert that a config based extensions support entry point syntax"""
    app = Flask(__name__)
    app.config["EXTENSIONS"] = [
        "example.dummy_flask_extension:dummy_instance.init_app"
    ]
    FlaskDynaconf(app, dynaconf_instance=settings)
    app.config.load_extensions()
    assert app.config.EXTENSIONS == [
        "example.dummy_flask_extension:dummy_instance.init_app"
    ]
    assert app.extensions["dummy"].__class__.__name__ == "DummyExtensionType"


def test_dynamic_load_exts_list(settings):
    """Assert that a config based extensions are loaded"""
    app = Flask(__name__)
    app.config["EXTENSIONS"] = ["example.dummy_flask_extension.dummy:init_app"]
    FlaskDynaconf(app, dynaconf_instance=settings, extensions_list=True)
    assert app.config.EXTENSIONS == [
        "example.dummy_flask_extension.dummy:init_app"
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
    assert app.config.HOSTNAME == "host.com"
    assert app.config.MY_VAR == "foo"

    assert app.config["HOSTNAME"] == "host.com"
    assert app.config["MY_VAR"] == "foo"

    assert app.config.get("HOSTNAME") == "host.com"
    assert app.config.get("MY_VAR") == "foo"

    assert app.config("HOSTNAME") == "host.com"
    assert app.config("MY_VAR") == "foo"


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
