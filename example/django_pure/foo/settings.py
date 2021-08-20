import os

# Where is all the Django's settings?
# Take a look at ../settings.yaml and ../.secrets.yaml
# Dynaconf supports multiple formats that files can be toml, ini, json, py
# Files are also optional, dynaconf can read from envvars, Redis or Vault.

# Build paths inside the project like this: os.path.join(settings.BASE_DIR, ..)
# Or use the dynaconf helper `settings.path_for('filename')`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = "/etc/foo/"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# 596
TEST_VALUE = "a"
