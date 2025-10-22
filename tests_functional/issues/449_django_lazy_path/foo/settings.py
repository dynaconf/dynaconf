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


# REAL CASE FOR PULP TESTING
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "foo_bar_original",
    ),
    "ANOTHER_DRF_KEY": "VALUE",
}


# HERE STARTS DYNACONF EXTENSION LOAD (Keep at the very bottom of settings.py)
# Read more at https://www.dynaconf.com/django/
import dynaconf  # noqa

settings = dynaconf.DjangoDynaconf(
    __name__,
    PRELOAD_FOR_DYNACONF=["../settings.yaml", "../.secrets.yaml"],
    ENVVAR_FOR_DYNACONF="PULP_SETTINGS",
)  # noqa
# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)

# test
assert settings.SERVER == "prodserver.com"
# assert settings.STATIC_URL == "/changed/in/settings.toml/by/dynaconf/"
assert settings.USERNAME == "admin_user_from_env"
assert settings.PASSWORD == "My5up3r53c4et"
assert settings.get("PASSWORD") == "My5up3r53c4et"
assert settings.FOO == "It overrides every other env"

assert settings.TEMPLATES[0]["DIRS"] == [
    f"{BASE_DIR}/templates"
], settings.TEMPLATES[0]["DIRS"]

ALLOWED_HOSTS = settings.get(
    "ALLOWED_HOSTS", ["::1", "127.0.0.1", "localhost"]
)
DUMMY_LIST = settings.get(
    "DUMMY_LIST",
    [
        "a",
        "dummy",
        "list",
    ],  # will be converted to a BoxList to keep the same API
)

# this is going to be a BoxList from yaml file
ALLOWED_HOSTS.to_list()

# this is going to be a list provided as default, but still with the same api.
DUMMY_LIST.to_list()
