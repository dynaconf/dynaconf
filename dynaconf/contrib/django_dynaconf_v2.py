"""Dynaconf django extension

In the `django_project/settings.py` put at the very botton of the file:

# HERE STARTS DYNACONF EXTENSION LOAD (Keep at the very bottom of settings.py)
# Read more at https://dynaconf.readthedocs.io/en/latest/guides/django.html
import dynaconf  # noqa
settings = dynaconf.DjangoDynaconf(__name__)  # noqa
# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)

Now in the root of your Django project
(the same folder where manage.py is located)

Put your config files `settings.{py|yaml|toml|ini|json}`
and or `.secrets.{py|yaml|toml|ini|json}`

On your projects root folder now you can start as::

    DJANGO_DEBUG='false' \
    DJANGO_ALLOWED_HOSTS='["localhost"]' \
    python manage.py runserver
"""
import os
import sys
import dynaconf

try:  # pragma: no cover
    from django import conf
    from django.conf import settings as django_settings
    django_installed = True
except ImportError:  # pragma: no cover
    django_installed = False


def load(django_settings_module_name=None, **kwargs):  # pragma: no cover
    if not django_installed:
        raise RuntimeError(
            "To use this extension django must be installed "
            "install it with: pip install django"
        )

    try:
        django_settings_module = sys.modules[django_settings_module_name]
    except KeyError:
        django_settings_module = sys.modules[
            os.environ['DJANGO_SETTINGS_MODULE']
        ]

    settings_file = os.path.abspath(django_settings_module.__file__)
    _root_path = os.path.dirname(settings_file)

    # 1) Create the lazy settings object reusing settings_module consts
    options = {
        k: v for k, v in django_settings_module.__dict__.items() if k.isupper()
    }
    options.update(kwargs)
    options.setdefault('SKIP_FILES_FOR_DYNACONF', [settings_file])
    options.setdefault('ROOT_PATH_FOR_DYNACONF', _root_path)
    options.setdefault('GLOBAL_ENV_FOR_DYNACONF', 'DJANGO')
    options.setdefault('ENV_SWITCHER_FOR_DYNACONF', 'DJANGO_ENV')
    lazy_settings = dynaconf.LazySettings(**options)

    # 2) Set all settings back to django_settings_module for 'django check'
    for setting_name, setting_value in lazy_settings._store.items():
        setattr(django_settings_module, setting_name.upper(), setting_value)

    # 3) keep django original settings
    dj = {}
    for key in dir(django_settings):
        if key.isupper() and key != 'SETTINGS_MODULE':
            dj[key] = getattr(django_settings, key, None)
        dj['ORIGINAL_SETTINGS_MODULE'] = django_settings.SETTINGS_MODULE

    lazy_settings.update(dj)

    # 4) Patch django.conf.settings
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
    return lazy_settings


# syntax sugar
DjangoDynaconf = load  # noqa
