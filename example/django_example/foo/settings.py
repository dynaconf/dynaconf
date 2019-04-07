import os

# Where is all the Django's settings?
# Take a look at ../settings.yaml and ../.secrets.yaml
# Dynaconf supports multiple formats that files can be toml, ini, json, py
# Files are also optional, dynaconf can read from envvars, Redis or Vault.

# Build paths inside the project like this: os.path.join(settings.BASE_DIR, ..)
# Or use the dynaconf helper `settings.path_for('filename')`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# HERE STARTS DYNACONF EXTENSION LOAD (Keep at the very bottom of settings.py)
# Read more at https://dynaconf.readthedocs.io/en/latest/guides/django.html
import dynaconf  # noqa
settings = dynaconf.DjangoDynaconf(__name__)  # noqa
# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)
