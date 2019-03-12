# Django Extension

Dynaconf extensions for Django works by patching the `settings.py` file with dynaconf loading hooks, the change is done on a single file and then in your whole project every time you call `django.conf.settings` you will have access to `dynaconf` attributes and methods.

## Initialize the extension

On the same directory where your `manage.py` is located run:

```bash
$ dynaconf init --django yourapp.settings
or
$ dynaconf init --django yourapp/settings.py
```

> NOTE: If you export the `DJANGO_SETTINGS_MODULE` then you can run only `dynaconf init` and it will find the file.

Dynaconf will append a patch to the bottom of your settings file.

Or you can manually append at the bottom of your django project's `settings.py` the following code:

```python
# HERE STARTS DYNACONF PATCHING

import os # noqa
import sys  # noqa
from dynaconf import LazySettings  # noqa

# For a list of config keys see:
# https://dynaconf.readthedocs.io/en/latest/guides/configuration.html
# Those keys can also be set as environment variables.
lazy_settings = LazySettings(
    # Configure this instance of Dynaconf
    GLOBAL_ENV_FOR_DYNACONF='DJANGO',
    ENV_FOR_DYNACONF=os.environ.get('DJANGO_ENV', 'DEVELOPMENT'),
    # Then rebind all settings defined above on this settings.py file.
    **{k: v for k, v in locals().items() if k.isupper()}
)


def __getattr__(name):  # noqa
    """This function will be used by Python 3.7+"""
    return getattr(lazy_settings, name)


def __dir__():  # noqa
    """This function will be used by Python 3.7+"""
    return dir(lazy_settings)


for setting_name, setting_value in lazy_settings._store.items():
    setattr(sys.modules[__name__], setting_name.upper(), setting_value)

# This import makes `django.conf.settings` to behave dynamically
import dynaconf.contrib.django_dynaconf # noqa

# HERE ENDS DYNACONF PATCHING
```

## Use `DJANGO_` environment variables

Then **django.conf.settings** will work as a `dynaconf.settings` instance and `DJANGO_` will be the global prefix to export environment variables.

Example:

```bash
export DJANGO_DEBUG=true     # django.conf.settings.DEBUG
export DJANGO_INTVALUE=1     # django.conf.settings['INTVALUE]
export DJANGO_HELLO="Hello"  # django.conf.settings.get('HELLO)
```

## Settings files

You can also have settings files for your Django app, in the root directory (the same where `manage.py` is located) put your `settings.toml` and `.secrets.toml` files and then define your environments `[default]`, `[development]` and `[production]`.

To switch the working environment the `DJANGO_ENV` variable can be used, so `DJANGO_ENV=development` to work
in development mode or `DJANGO_ENV=production` to switch to production.

> **IMPORTANT**: To use `$ dynaconf` CLI the `DJANGO_SETTINGS_MODULE` must be defined.

IF you don't want to manually create your config files take a look at the [CLI](cli.html)

> **NOTE**: It is recommended that all the **django's** internal config vars should be kept in the `settings.py` of your project, then application specific values you can  place in dynaconf's `settings.toml` in the root (same folder as manage.py). You can override settings.py values in the dynaconf settings file as well.

## Customizations

It is possible to customize how your django project will load settings, example: You want your users to customize a settings file defined in `export PROJECTNAME_SETTINGS=/path/to/settings.toml` and you want environment variables to be loaded from `PROJECTNAME_VARNAME`

Edit django `settings.py` and modify the dynaconf patch part:

```python
...
lazy_settings = LazySettings(
    # Configure this instance of Dynaconf
    GLOBAL_ENV_FOR_DYNACONF='PROJECTNAME',
    ENV_FOR_DYNACONF=os.environ.get('PROJECTNAME_ENV', 'DEVELOPMENT'),
    ENVVAR_FOR_DYNACONF='PROJECTNAME_SETTINGS',
    # Then rebind all settings defined above on this settings.py file.
    **{k: v for k, v in locals().items() if k.isupper()}
)
...
```

Then the working environment can now be switched using `export PROJECTNAME_ENV=production`

And you can have user to define custom config files on `export PROJECTNAME_SETTINGS=/other/path/to/settings.py{yaml,toml,json,ini}`

And users can set variables on environment like `export PROJECTNAME_DEBUG=true`

## Deprecation note

On old dynaconf releases the solution was to add `dynaconf.contrib.django_dynaconf` to `INSTALLED_APPS` as the first item, this still works but has some limitations so it is not recommended anymore.
