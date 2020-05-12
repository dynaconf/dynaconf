from dynaconf import LazySettings

settings = LazySettings(envless_mode=True, lowercase_read=True)

assert settings.server == "foo.com"
assert settings.SERVER == "foo.com"
assert settings["SERVER"] == "foo.com"
assert settings["server"] == "foo.com"
assert settings("SERVER") == "foo.com"
assert settings("server") == "foo.com"
assert settings.get("SERVER") == "foo.com"
assert settings.get("server") == "foo.com"
