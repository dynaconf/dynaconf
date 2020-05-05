# WARNING: THIS EXTENSION IS DEPRECATED in favor of django_dynaconf_v2
# Read more on how to integrate with django on
# https://dynaconf.readthedocs.io/en/latest/guides/django.html
import os

from django.conf import settings as django_settings

from dynaconf import LazySettings

dj = {}

for key in dir(django_settings):
    if key.isupper() and key != "SETTINGS_MODULE":
        dj[key] = getattr(django_settings, key, None)
    dj["ORIGINAL_SETTINGS_MODULE"] = django_settings.SETTINGS_MODULE

dj.setdefault("ENVVAR_PREFIX", "DJANGO")
env_prefix = f"{dj['ENVVAR_PREFIX']}_ENV"  # DJANGO_ENV
dj.setdefault("ENV", os.environ.get(env_prefix, "DEVELOPMENT").upper())

settings = LazySettings(**dj)
