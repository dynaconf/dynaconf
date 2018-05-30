# Django Extension

Dynaconf a drop in replacement to `django.conf.settings`.

Following [this pattern recommended pattern](https://mail.python.org/pipermail/python-ideas/2012-May/014969.html)
this extension makes your Django's `conf.settings` in to a `dynaconf` instance.

## Initialize the extension

In your django project's `settings.py` include:

```python
INSTALLED_APPS = [
    'dynaconf.contrib.django_dynaconf',
    ...
]
```

> **NOTE**: The extension must be included as the first INSTALLED_APP of the list

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
