import os
import sys

import dynaconf


def test_djdt_382(tmpdir):
    settings_file = tmpdir.join("settings.py")
    settings_file.write("SECRET_KEY = 'dasfadfds2'")
    tmpdir.join("__init__.py").write("")
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
    settings = dynaconf.DjangoDynaconf(__name__, environments=True)
    settings.configure(settings_module="settings")
    assert settings.SECRET_KEY == "dasfadfds2"
    assert settings.is_overridden("FOO") is False
