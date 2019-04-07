import os

# Where is all the Django's settings?
# Take a look at ../settings.yaml and ../.secrets.yaml
# Dynaconf supports multiple formats that files can be toml, ini, json, py
# Files are also optional, dynaconf can read from envvars, Redis or Vault.

# Build paths inside the project like this: os.path.join(settings.BASE_DIR, ..)
# Or use the dynaconf helper `settings.path_for('filename')`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# HERE STARTS DYNACONF EXTENSION LOAD
# Important! Keep it at the very bottom of your Django's settings.py file
# Read more at https://dynaconf.readthedocs.io/en/latest/guides/django.html
# Tip: All the variables defined above can now be moved to
# `../settings.{toml,yaml,json,ini}` under `[default]` section.
import os, dynaconf  # noqa
# dynaconf.default_settings.AUTO_LOAD_DOTENV = False  # noqa
# dynaconf.default_settings.start_dotenv(root_path=os.path.dirname(os.path.abspath(__file__)))  # noqa
settings = dynaconf.DjangoDynaconf(__name__)  # noqa
# Important! No more code below this line
# HERE ENDS DYNACONF EXTENSION LOAD
