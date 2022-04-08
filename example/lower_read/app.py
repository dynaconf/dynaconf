from dynaconf import Dynaconf

settings = Dynaconf(settings_files="settings.yaml")

assert settings.server == "foo.com"
assert settings.SERVER == "foo.com"
assert settings["SERVER"] == "foo.com"
assert settings["server"] == "foo.com"
assert settings("SERVER") == "foo.com"
assert settings("server") == "foo.com"
assert settings.get("SERVER") == "foo.com"
assert settings.get("server") == "foo.com"
