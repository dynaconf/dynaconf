# coding: utf-8
import django
from dynaconf import LazySettings


django_settings = {}
for key in dir(django.conf.settings):
    if key.isupper():
        django_settings[key] = getattr(django.conf.settings, key, None)


django_settings['SETTINGS_MODULE'] = django_settings.get(
    'DYNACONF_SETTINGS_MODULE', 'settings.yml'
)

django.conf.settings = LazySettings(**django_settings)
