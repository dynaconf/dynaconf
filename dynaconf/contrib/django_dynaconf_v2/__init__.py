"""Dynaconf django extension

In the `django_project/settings.py` put at the botton:

# HERE STARTS DYNACONF PATCHING
import os  # noqa
import sys  # noqa
import dynaconf  # noqa
_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dynaconf.default_settings.AUTO_LOAD_DOTENV = False  # noqa
dynaconf.default_settings.start_dotenv(root_path=_ROOT_PATH)

# For a list of config keys see:
# https://dynaconf.readthedocs.io/en/latest/guides/configuration.html
# Those keys can also be set as environment variables.
lazy_settings = dynaconf.LazySettings(
    # Configure this instance of Dynaconf
    GLOBAL_ENV_FOR_DYNACONF='DJANGO',
    ENV_FOR_DYNACONF=os.environ.get('DJANGO_ENV', 'DEVELOPMENT'),
    ROOT_PATH_FOR_DYNACONF=_ROOT_PATH,
    # Then rebind all settings defined above on this settings.py file.
    **{k: v for k, v in locals().items() if k.isupper()}
)

# This makes django check happy because all settings is provided
for setting_name, setting_value in lazy_settings._store.items():
    setattr(sys.modules[__name__], setting_name.upper(), setting_value)

# This import makes `django.conf.settings` to behave dynamically
from dynaconf.contrib import django_dynaconf_v2  # noqa
django_dynaconf_v2.load(lazy_settings)
# HERE ENDS DYNACONF PATCHING

Now in the root of your Django project
(the same folder where manage.py is located)

Put your config files `settings.{py|yaml|toml|ini|json}`
and or `.secrets.{py|yaml|toml|ini|json}`

On your projects root folder now you can start as::

    DJANGO_DEBUG='@bool false' \
    DJANGO_ALLOWED_HOSTS='@json ["localhost"]' \
    python manage.py runserver
"""

import sys  # pragma: no cover
from django import conf  # pragma: no cover
from django.conf import settings as django_settings  # pragma: no cover


def load(lazy_settings):  # pragma: no cover
    dj = {}
    for key in dir(django_settings):
        if key.isupper() and key != 'SETTINGS_MODULE':
            dj[key] = getattr(django_settings, key, None)
        dj['ORIGINAL_SETTINGS_MODULE'] = django_settings.SETTINGS_MODULE

    dj.setdefault('GLOBAL_ENV_FOR_DYNACONF', 'DJANGO')

    lazy_settings.update(dj)

    class Wrapper(object):

        # lazy_settings = conf.settings.lazy_settings

        def __getattribute__(self, name):
            if name == 'settings':
                return lazy_settings
            else:
                return getattr(conf, name)

    # This implementation is recommended by Guido Van Rossum
    # https://mail.python.org/pipermail/python-ideas/2012-May/014969.html
    sys.modules['django.conf'] = Wrapper()
