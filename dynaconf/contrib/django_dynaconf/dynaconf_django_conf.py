# WARNING: THIS EXTENSION IS DEPRECATED
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


dj.setdefault("ENVVAR_PREFIX_FOR_DYNACONF", "DJANGO")

env_prefix = "{0}_ENV".format(dj["ENVVAR_PREFIX_FOR_DYNACONF"])  # DJANGO_ENV

dj.setdefault(
    "ENV_FOR_DYNACONF", os.environ.get(env_prefix, "DEVELOPMENT").upper()
)

settings = LazySettings(**dj)
