from __future__ import annotations

import os
import sys

import dynaconf


def test_djdt_382(tmpdir):
    settings_file = tmpdir.join("settings.py")
    settings_file.write("\n".join(["SECRET_KEY = 'dasfadfds2'"]))
    tmpdir.join("__init__.py").write("")
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
    sys.path.append(str(tmpdir))
    __import__("settings")
    settings = dynaconf.DjangoDynaconf("settings", environments=True)
    settings.configure(settings_module="settings")
    assert settings.SECRET_KEY == "dasfadfds2"
    assert settings.is_overridden("FOO") is False


def test_override_settings_596(tmpdir):
    settings_file = tmpdir.join("other_settings.py")
    settings_file.write("\n".join(["SECRET_KEY = 'abcdef'"]))
    tmpdir.join("__init__.py").write("")
    os.environ["DJANGO_SETTINGS_MODULE"] = "other_settings"
    sys.path.append(str(tmpdir))
    __import__("other_settings")
    settings = dynaconf.DjangoDynaconf("other_settings", environments=True)
    settings.configure(settings_module="other_settings")
    assert settings.SECRET_KEY == "abcdef"

    # mimic what django.test.utils.override_settings does
    class UserSettingsHolder(dynaconf.LazySettings):
        _django_override = True

    override = UserSettingsHolder(settings._wrapped)
    override.SECRET_KEY = "foobar"

    # overridden settings is changed
    assert override.SECRET_KEY == "foobar"

    # original not changed
    assert settings.SECRET_KEY == "abcdef"
