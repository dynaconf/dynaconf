from dynaconf import LazySettings
from django.conf import settings as django_settings


dj = {}
for key in dir(django_settings):
    if key.isupper() and key != 'SETTINGS_MODULE':
        dj[key] = getattr(django_settings, key, None)
    dj['ORIGINAL_SETTINGS_MODULE'] = django_settings.SETTINGS_MODULE


settings = LazySettings(
    NAMESPACE_FOR_DYNACONF='DYNACONF',
    **dj
)
