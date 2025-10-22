from __future__ import annotations

import os

# Where is all the Django's settings?
# Take a look at ../settings.yaml and ../.secrets.yaml
# Dynaconf supports multiple formats that files can be toml, ini, json, py
# Files are also optional, dynaconf can read from envvars, Redis or Vault.

# Build paths inside the project like this: os.path.join(settings.BASE_DIR, ..)
# Or use the dynaconf helper `settings.path_for('filename')`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = "/etc/foo"

# HERE STARTS DYNACONF EXTENSION LOAD (Keep at the very bottom of settings.py)
# Read more at https://www.dynaconf.com/django/
import dynaconf  # noqa

settings_location = os.path.join(
    BASE_DIR, "config/settings.yaml,config/.secrets.yaml"
)

settings = dynaconf.DjangoDynaconf(
    __name__,
    ENVIRONMENTS_FOR_DYNACONF=True,
    GLOBAL_ENV_FOR_DYNACONF="MYWEBAPP",
    ENV_SWITCHER_FOR_DYNACONF="MYWEBAPP_ENV",
    SETTINGS_MODULE_FOR_DYNACONF=settings_location,
    INCLUDES_FOR_DYNACONF=[os.path.join(BASE_DIR, "includes/*")],
    ENVVAR_FOR_DYNACONF="MYWEBAPP_SETTINGS",
)  # noqa
# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)


# test
assert (
    settings.ENVVAR_PREFIX_FOR_DYNACONF == "MYWEBAPP"
), settings.ENVVAR_PREFIX_FOR_DYNACONF
assert settings.GLOBAL_ENV_FOR_DYNACONF == "MYWEBAPP"
assert settings.PLUGIN_ENABLED is True
assert settings.PLUGIN_LIST == ["plugin1", "plugin2"]


assert settings.SERVER == "prodserver.com"
assert settings.STATIC_URL == "/changed/in/settings.toml/by/dynaconf/"
assert settings.USERNAME == "admin_user_from_env"
assert settings.PASSWORD == "My5up3r53c4et"
assert settings.get("PASSWORD") == "My5up3r53c4et"
assert settings.FOO == "It overrides every other env"
assert settings.DATABASES.DEFAULT.NAME == "db.sqlite3"


assert settings.SETTINGS_FILE_FOR_DYNACONF == settings_location
assert (
    settings.SETTINGS_MODULE_FOR_DYNACONF == settings_location
), settings.SETTINGS_MODULE_FOR_DYNACONF
assert settings.SETTINGS_MODULE == settings_location
assert (
    settings.DYNACONF_SETTINGS == settings_location
), settings.DYNACONF_SETTINGS
assert settings.settings_module == settings_location
