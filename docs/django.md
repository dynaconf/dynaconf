# Django

Built-in integration with Django.

## Overview

Dynaconf can integrate with Django in two ways:

- [Explicit Mode](#explicit-mode): Use dynaconf to load and merge data from multiple sources but settings control keeps with Django.
    - Choose this if you want to fine control your settings, then use dynaconf only to populate your `settings.py`.
      Keep in mind that on this mode you do not gain the [Extra Functionalities](#extra-functionalities) from dynaconf.
- [Django Extension](#django-extension): Give full control of `django.conf.settings` to Dynaconf
    - Choose this if you want to have access to all dynaconf features across the whole django application, with some [trade-offs](#known-caveats)

In both modes Dynaconf will be able to load variables from multiple sources (env vars, settings files in multiple formats)
and perform the usual parsing, merging and validation and optionally  execute defined hooks.

## Integration Modes

### Explicit mode

Some users prefer to explicitly load each setting variable inside the `settings.py` and then let django manage it in the usual way. This is possible, but keep in mind that doing so will prevent the usage of dynaconf methods like `using_env`, `get`, etc.

Dynaconf will be available only on `settings.py` scope. On the rest of your application, settings are managed by Django normally.


#### Setup

Edit your `<app>/settings.py`

```py title="settings.py"
# At the top of the file:
import sys
from pathlib import Path
from dynaconf import Dynaconf, Validator

validators = [
    Validator("INSTALLED_APPS", cont="mynew.app"),
    Validator("DEBUG", ne=True, env="production"),
]
settings = Dynaconf(
    validators=validators,  # Raises ValidationError for passed in validators
    settings_files=["/etc/myapp/settings.toml"]  # .py, .yaml, .ini, .json etc..
)

# Common Django settings
# ...
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    ...
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# ...

# At the end of your settings.py
settings.populate_obj(sys.modules[__name__])
```

!!! info
    `populate_obj` accepts the following arguments:
    - `ignore`: Don't override local variables, only add new ones.
    (added in `2.1.1`)
    - `merge`: same as passing `merge_enabled=True` to Dynaconf
    - `merge_unique`: don't duplicate items in lists. (this can also be controlled individually on each variable)
    (added in 3.3.0)

#### Usage

The `Dynaconf` instance will load and parse all settings from your settings sources and
then `populate_obj` will merge the loaded data with local settings variables.

At the end your `django.conf.settings` is just a regular Django Settings.

```python
from django.conf import settings
assert "mynew.app" in settings.INSTALLED_APPS  # True: Merged from the toml file
```

### Django Extension

This mode is different from the Explicit Mode explained above, on this mode Dynaconf will
automatically take lots of decisions and full control over your `django.conf.settings`

It works by patching the `settings.py` file with dynaconf loading hooks, the change is done on a single file and then in your whole project. Every time you call `django.conf.settings` you will have access to `dynaconf` attributes and methods.


#### Extra functionalities

On this mode you can still use the same settings file formats and sources, the main difference
is that now every time you import `settings` it is a Dynaconf instance and you gain some
extra functionalities like:

- Dict like access: `settings["KEY"]`
- Get method: `settings.get("KEY", default)`
- Dotted dict access: `settings["DATABASES.default.name"]`
- Attribute access: `settings.databases.default.name`
- Case insensitivity: `settings.databases == settings.DATABASES`
- Context manager: `with settings.using_env("testing"):`
- Temporary settings copy `settings = settings.clone(foo=bar)`
- Real time hooks: `settings.MY_SPECIAL_KEY` triggers a custom `get_special_key_value() -> value` function at access time.

Those features comes with a price that you can see on [known caveats](#known-caveats)

#### Setup

You can manually append at the very bottom of your django project's `settings.py` the following code:

```python title="settings.py"

# Common django default settings comes here
DEBUG = True
...

# Then at the very bottom of settings.py

# HERE STARTS DYNACONF EXTENSION LOAD (Keep at the very bottom of settings.py)
# Read more at https://www.dynaconf.com/django/
import dynaconf
validators = [
    dynaconf.Validator("INSTALLED_APPS", cont="mynew.app"),
    dynaconf.Validator("DEBUG", ne=True, env="production"),
]
settings = dynaconf.DjangoDynaconf(
    __name__,
    settings_files=["/etc/myapp/settings.toml"],
    validators=validators,
)
# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)
```

!!! tip
    Take a look at [tests_functional/django_example](https://github.com/dynaconf/dynaconf/tree/master/tests_functional/legacy/django_example)

#### Known Caveats

- If `settings.configure()` is called directly it disables Dynaconf, use `settings.DYNACONF.configure()`
- Inside the settings file `<app>/settings.py` and `<app>/dynaconf_hooks.py` it is not possible to use
  translation functions such as `gettext` and `gettext_lazy`, those functions works normally on any part
  of the application except the settings files due to a lifecycle limitation, if you want to use translation
  tools inside the `<app>/settings.py` file you have to opt to [dynaconf explicit mode](#explicit-mode).
- Pylint-Django may raise linting error for [dynaconf_merge markers](https://github.com/dynaconf/dynaconf/issues/578)


## Settings Sources

Besides the common `<app>/settings.py` you will be able to load extra settings
from defined locations, can be a single file, multiple files or even a glob pattern,
the variables from those extra sources will be merged with the variables from
the main app settings and the merging can be controlled individually with markers.

Choose the format that best suits your needs and preferences.

### Common Sources

=== "python"

    ```python title="/etc/myapp/settings.py"
    DEBUG = false
    ADMIN_NAMESPACE = "admin"
    LOGIN_URL = "@reverse_lazy @format {this.ADMIN_NAMESPACE}:login"
    INSTALLED_APPS = "@merge my_new.app,otherapp"
    # ALTERNATIVELY
    INSTALLED_APPS = ["mynew.app", "otherapp", "dynaconf_merge"]

    LOGGING__handlers__console__formatter = "simple"
    # ALTERNATIVELY
    LOGGING = {"handlers": {"console": {"formatter":"simple"}}, "dynaconf_merge": true}

    DATABASES__default = {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite"}
    # ALTERNATIVELY
    DATABASES__default__ENGINE = "django.db.backends.sqlite3"
    DATABASES__default__NAME = "db.sqlite"

    AUTH_PASSWORD_VALIDATORS = [
        {"name": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"name": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    ]
    ```

=== "toml"

    ```toml title="/etc/myapp/settings.toml"
    DEBUG = false
    ADMIN_NAMESPACE = "admin"
    LOGIN_URL = "@reverse_lazy @format {this.ADMIN_NAMESPACE}:login"

    INSTALLED_APPS = "@merge my_new.app,otherapp"
    # ALTERNATIVELY
    INSTALLED_APPS = ["mynew.app", "otherapp", "dynaconf_merge"]

    LOGGING__handlers__console__formatter = "simple"
    # ALTERNATIVELY
    LOGGING = {handlers={console={formatter="simple"}}, dynaconf_merge=true}

    [DATABASES.default]
    ENGINE = "django.db.backends.sqlite3"
    NAME = "db.sqlite"
    # ALTERNATIVELY
    DATABASES__default__ENGINE = "django.db.backends.sqlite3"
    DATABASES__default__NAME = "db.sqlite"

    [[AUTH_PASSWORD_VALIDATORS]]
    NAME = "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"

    [[AUTH_PASSWORD_VALIDATORS]]
    NAME = "django.contrib.auth.password_validation.MinimumLengthValidator"
    ```

=== "yaml"

    ```yaml title="/etc/myapp/settings.yaml"
    DEBUG: false
    ADMIN_NAMESPACE: "admin"
    LOGIN_URL: "@reverse_lazy @format {this.ADMIN_NAMESPACE}:login"

    INSTALLED_APPS: "@merge my_new.app,otherapp"
    # ALTERNATIVELY
    INSTALLED_APPS:
     - "mynew.app"
     - "otherapp"
     - "dynaconf_merge"

    LOGGING__handlers__console__formatter: "simple"
    # ALTERNATIVELY
    LOGGING:
      dynaconf_merge: true
      handlers:
        console:
          formatter: "simple"

    DATABASES:
      default:
        ENGINE: "django.db.backends.sqlite3"
        NAME: "db.sqlite"
    # ALTERNATIVELY
    DATABASES__default__ENGINE: "django.db.backends.sqlite3"
    DATABASES__default__NAME: "db.sqlite"

    AUTH_PASSWORD_VALIDATORS
      - NAME: "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
      - NAME: "django.contrib.auth.password_validation.MinimumLengthValidator"
    ```

=== "environment variables"

    ```bash
    export DJANGO_ENV=production

    export DJANGO_DEBUG=false
    export DJANGO_ADMIN_NAMESPACE="admin"
    export DJANGO_LOGIN_URL="@reverse_lazy @format {this.ADMIN_NAMESPACE}:login"

    export DJANGO_INSTALLED_APPS="@merge my_new.app,otherapp"
    # ALTERNATIVELY
    export DJANGO_INSTALLED_APPS='["mynew.app", "otherapp", "dynaconf_merge"]'

    export DJANGO_LOGGING__handlers__console__formatter="simple"
    # ALTERNATIVELY
    export DJANGO_LOGGING='@json {"handlers": {"console": {"formatter": "simple"}}, "dynaconf_merge": true}'

    export DJANGO_DATABASES__default__ENGINE: "django.db.backends.sqlite3"
    export DJANGO_DATABASES__default__NAME: "db.sqlite"
    # ALTERNATIVELY
    export DJANGO_DATABASES__default='@json {"NAME": "db.sqlite", "ENGINE": "dj.."}'

    export DJANGO_AUTH_PASSWORD_VALIDATORS___0__NAME="django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    export DJANGO_AUTH_PASSWORD_VALIDATORS___1__NAME="django.contrib.auth.password_validation.MinimumLengthValidator"
    # ALTERNATIVELY
    export DJANGO_AUTH_PASSWORD_VALIDATORS='[{NAME="dj..."}, {NAME="dj..."}]'
    ```

### Other Sources

Dynaconf also supports **JSON**, **INI**, **REDIS**, **HASHICORP VAULT** and custom loaders.


### Using `DJANGO_` environment variables

Then **django.conf.settings** will work as a `dynaconf.settings` instance and `DJANGO_` will be the global prefix to export environment variables.

Example:

```bash
export DJANGO_DEBUG=true     # django.conf.settings.DEBUG
export DJANGO_INTVALUE=1     # django.conf.settings['INTVALUE']
export DJANGO_HELLO="Hello"  # django.conf.settings.get('HELLO')
```

!!! tip
    If you don't want to use `DJANGO_` as prefix for envvars you can customize by passing a new name e.g: `dynaconf.DjangoDynaconf(__name__, ENVVAR_PREFIX_FOR_DYNACONF="FOO")` then `export FOO_DEBUG=true`

</br>

You can also set nested dictionary values. For example, let's say you have a configuration like this:

```py
# settings.py

...
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'module.foo.engine',
        'ARGS': {'timeout': 30}
    }
}
...
```

And  now you want to change the values of `ENGINE` to `other.module`, via environment variables you can use the format `${ENVVAR_PREFIX}_${VARIABLE}__${NESTED_ITEM}__${NESTED_ITEM}`

Each `__` (dunder, a.k.a *double underline*) denotes access to nested elements in a dictionary.

So:

```bash
export DYNACONF_DATABASES__default__ENGINE=other.module
```

will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'timeout': 30}
    }
}
```

!!! warning
    Notice that casing is important for Django settings, so `DYNACONF_DATABASES__default__ENGINE` is not the same as `DYNACONF_DATABASES__DEFAULT__ENGINE` you must use the first which matched the proper django settings.

Read more on [environment variables](https://www.dynaconf.com/merging/#nested-keys-in-dictionaries-via-environment-variables)

### Using Settings files

You can also have settings files for your Django app.

In the root directory (the same where `manage.py` is located) put your `settings.{yaml, toml, ini, json, py}` and `.secrets.{yaml, toml, ini, json, py}` files and then define your environments `[default]`, `[development]` and `[production]`.

To switch the working environment the `DJANGO_ENV` variable can be used, so `DJANGO_ENV=development` to work
in development mode or `DJANGO_ENV=production` to switch to production.

!!! tip
    **.yaml** is the recommended format for Django applications because it allows easily writing complex data structures. Nevertheless, feel free to choose any format you are familiar with.

!!! warning "Important"
    To use `$ dynaconf` CLI the `DJANGO_SETTINGS_MODULE` environment variable must be defined.

## Customizations

### Loading settings

It is possible to customize how your django project will load settings.

Example: you want your users to customize a settings file defined in `export PROJECTNAME_SETTINGS=/path/to/settings.toml` and you want environment variables to be loaded from `PROJECTNAME_VARNAME`

To achieve that, edit django `settings.py` and modify the dynaconf extension part:

from:

```python
# HERE STARTS DYNACONF EXTENSION LOAD
...
settings = dynaconf.DjangoDynaconf(__name__)
# HERE ENDS DYNACONF EXTENSION LOAD
```

to:

```python
# HERE STARTS DYNACONF EXTENSION LOAD
...
settings = dynaconf.DjangoDynaconf(
    __name__,
    ENVVAR_PREFIX_FOR_DYNACONF='PROJECTNAME',
    ENV_SWITCHER_FOR_DYNACONF='PROJECTNAME_ENV',
    SETTINGS_FILE_FOR_DYNACONF='/etc/projectname/settings.toml',
    ENVVAR_FOR_DYNACONF='PROJECTNAME_SETTINGS',
    INCLUDES_FOR_DYNACONF=['/etc/projectname/plugins/*'],
)
# HERE ENDS DYNACONF EXTENSION LOAD
```

Variables on environment can be set/override using `PROJECTNAME_` prefix e.g: `export PROJECTNAME_DEBUG=true`.

The working environment can now be switched using `export PROJECTNAME_ENV=production` it defaults to `development`.

Your settings are now read from `/etc/projectname/settings.toml` (dynaconf will not perform search for all the settings formats). This settings location can be changed via envvar using `export PROJECTNAME_SETTINGS=/other/path/to/settings.py{yaml,toml,json,ini}`

You can have additional settings read from `/etc/projectname/plugins/*` any supported file from this folder will be loaded.

You can set more options, take a look at [configuration](configuration.md)

### Use Django functions inside custom settings

If you need to use django functions inside your settings, you can register custom
converters with the `add_converters` utility.

When defining those in `settings.py`, there are some django functions that can't
be imported directly in the module scope. Because of that, you may add them in
a [hook](advanced.md#hooks) that executes after loading.

For example, if you need to use `reverse_lazy`, you might do this:

```python
# myprj/settings.py

import dynaconf

def converters_setup():
    from django.urls import reverse_lazy  # noqa

    dynaconf.add_converter("reverse_lazy", reverse_lazy)

settings = dynaconf.DjangoDynaconf(__name__, post_hooks=converters_setup)

# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)
```

And then the following code would work:

```yaml
# settings.yaml

default:
    ADMIN_NAMESPACE: admin
    LOGIN_URL: "@reverse_lazy @format {this.ADMIN_NAMESPACE}:login"
```

!!! note
    Some common converters may be added to Dynaconf in future releases. See [#865](https://github.com/dynaconf/dynaconf/issues/865)

    For `gettext`, see [#648](https://github.com/dynaconf/dynaconf/issues/648)

## Reading Settings on Standalone Scripts

The recommended way to create standalone scripts is by creating `management commands` inside your Django applications or plugins.

The examples below assume you have `DJANGO_SETTINGS_MODULE` environment variable set, either by `exporting` it to your env or by explicitly adding it to `os.environ` dictionary.

!!! tip "Important"
    If you need the script to be available out of your Django Application Scope, prefer using `settings.DYNACONF.configure()` instead of the common `settings.configure()` provided by Django. The latter would cause dynaconf to be disabled.</br></br>
    After all, you probably don't need to call it, as you have `DJANGO_SETTINGS_MODULE` exported.

### Common case

```python
# /etc/my_script.py

from django.conf import settings
print(settings.DATABASES)
```

### Explicitly adding the setting module

```python
# /etc/my_script.py

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'foo.settings'

from django.conf import settings
print(settings.DATABASES)
```

### When you need the `configure`

Calling `DYNACONF.configure()` is needed when you want to access dynaconf special methods like `using_env`, `get`, `get_fresh` etc...

```python
# /etc/my_script.py

from django.conf import settings
settings.DYNACONF.configure()
print(settings.get('DATABASES'))
```

### Importing settings directly

This is recommended for the above case.

```python
# /etc/my_script.py

from foo.settings import settings
print(settings.get('DATABASES'))
```

### Importing settings via importlib

```python
# /etc/my_script.py

import os
import importlib
settings = importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
print(settings.get('DATABASES'))
```

## Testing on Django

Django testing must work out of the box!

### Mocking envvars with django

But in some cases when you `mock` stuff and need to add `environment variables` to `os.environ` on demand for test cases it may be needed to `reload` the `dynaconf`.

To do that, write up your test case setup part:

```py
import os
import importlib
from myapp import settings # NOTE: this uses your app module not django.conf

class TestCase(...):
    def setUp(self):
        os.environ['DJANGO_FOO'] = 'BAR'  # dynaconf should read it and set `settings.FOO`
        importlib.reload(settings)

    def test_foo(self):
        self.assertEqual(settings.FOO, 'BAR')
```

### Using pytest and django

Install `pip install pytest-django`

Add to your conftest.py

`project/tests/conftest.py`
```py
import pytest

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    # https://github.com/dynaconf/dynaconf/issues/491#issuecomment-745391955
    from django.conf import settings
    settings.setenv('testing')  # force the environment to be whatever you want
```

## Deprecation note

On old dynaconf releases the solution was to add `dynaconf.contrib.django_dynaconf` to `INSTALLED_APPS` as the first item. This still works but has some limitations so it is not recommended anymore.
