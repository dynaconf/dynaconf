from __future__ import annotations


def test_dynaconf_is_on_testing_env(app):
    assert app.config["VALUE"] == "On Testing"
    assert app.config.current_env == "testing"


def test_dynaconf_settings_is_the_same_object(app):
    from dynaconf import settings

    assert settings is app.config._settings
    assert app.config["VALUE"] == settings.VALUE
    assert app.config.current_env == settings.current_env
