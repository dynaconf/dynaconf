import os
import sys

import dynaconf


def test_djdt_382(tmpdir):
    sys.path.insert(0, str(tmpdir))
    settings_file = tmpdir.join("settings.py")
    settings_file.write("SECRET_KEY = 'dasfadfds'")
    tmpdir.join("__init__.py").write("")
    os.environ["DJANGO_SETTINGS_MODULE"] = str("settings")
    settings = dynaconf.DjangoDynaconf(__name__, environments=True)
    settings.configure(settings_module=__file__)
    assert settings.is_overridden("FOO") is False
