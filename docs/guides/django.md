# Django Extension

Dynaconf a drop in replacement to `django.conf.settings`.

Following [this pattern recommended pattern](https://mail.python.org/pipermail/python-ideas/2012-May/014969.html)
this extension makes your Django's `conf.settings` in to a `dynaconf` instance.

## Initialize the extension

In your django project's `settings.py` include:

```python
# *Django `check` requires this before loading isntalled apps, this can be overwriten by dynaconf later
SECRET_KEY = True  

# Load dynaconf
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

## Customizations

It is possible to customize how your django project will load settings, example: You want your users to customize a settings file defined in `export PROJECTNAME_SETTINGS=/path/to/settings.toml` and you want environment variables to be loaded from `PROJECTNAME_VARNAME`

your django `settings.py`

```python
SECRET_KEY = True
"""Django `check` requires the SECRET_KEY to exist before initialing
INSTALLED_APPS this value is set to True but will be overwritten after by the
value exported as PROJECTNAME_SECRET_KEY or defined in the file PROJECTNAME_SETTINGS"""

GLOBAL_ENV_FOR_DYNACONF = "PROJECTNAME"
"""This defines which environment variable global prefix dynaconf will load
That means that `export PROJECTNAME_FOO=1` will be loaded to `django.conf.settings.FOO
On command line it is possible to check it with `dynaconf list -k foo`"""

ENVVAR_FOR_DYNACONF = "PROJECTNAME_SETTINGS"
"""This defines which path dynaconf will look to load config files
example: export PROJECTNAME_SETTINGS=/path/to/settings.toml and the format can be
.ini, .json, .yaml or .toml

e.g::

    export PROJECTNAME_SETTINGS=settings.toml
    [default]
    FOO = 1
    [development]
    FOO = 2
    [production]
    FOO = 3


OR::

    export PROJECTNAME_SETTINGS=settings.yaml
    default:
      foo: 1
    development:
      foo: 2
    production:
      foo: 3


It is also possible to pass a list of files::

    export PROJECTNAME_SETTINGS=settings.toml,other_settings.yaml,another.json

The variables will be cascaded in the defined order (last wins the precedence)
The environment variables wins precedence over all!
"""

# load dynaconf
INSTALLED_APPS = [
    'dynaconf.contrib.django_dynaconf',
    ...
]
```

Then the working environment can now be switched using `export PROJECTNAME_ENV=production`
