# Django Extension

> **New in 2.0.0**

Dynaconf extension for Django works by patching the `settings.py` file with dynaconf loading hooks, the change is done on a single file and then in your whole project. Every time you call `django.conf.settings` you will have access to `dynaconf` attributes and methods.

Ensure dynaconf is installed on your env `pip install dynaconf[yaml]`

## Initialize the extension

You can manually append at the bottom of your django project's `settings.py` the following code:

```python
# HERE STARTS DYNACONF EXTENSION LOAD (Keep at the very bottom of settings.py)
# Read more at https://www.dynaconf.com/django/
import dynaconf  # noqa
settings = dynaconf.DjangoDynaconf(__name__)  # noqa
# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)
```

Or **optionally** you can, on the same directory where your `manage.py` is located run:

```bash
export DJANGO_SETTINGS_MODULE=yourapp.settings
$ dynaconf init

# or passing the location of the settings file

$ dynaconf init --django yourapp/settings.py

```

Dynaconf will append its extension loading code to the bottom of your `yourapp/settings.py` file and will create `settings.toml` and `.secrets.toml` in the current folder (the same where `manage.py` is located).

!!! tip
    Take a look at [tests_functional/django_example](https://github.com/dynaconf/dynaconf/tree/master/tests_functional/django_example)

## Using `DJANGO_` environment variables

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

## Settings files

You can also have settings files for your Django app.

In the root directory (the same where `manage.py` is located) put your `settings.{yaml, toml, ini, json, py}` and `.secrets.{yaml, toml, ini, json, py}` files and then define your environments `[default]`, `[development]` and `[production]`.

To switch the working environment the `DJANGO_ENV` variable can be used, so `DJANGO_ENV=development` to work
in development mode or `DJANGO_ENV=production` to switch to production.

If you don't want to manually create your config files take a look at the [CLI](cli.md)

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

## Mocking envvars with django

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

## Using pytest and django

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

## Explicit mode

Some users prefer to explicitly load each setting variable inside the `settings.py` and then let django manage it in the usual way. This is possible, but keep in mind that doing so will prevent the usage of dynaconf methods like `using_env`, `get`.

Dynaconf will be available only on `settings.py` scope. On the rest of your application, settings are managed by Django normally.

```py
# settings.py

import sys
from dynaconf import LazySettings

settings = LazySettings(**YOUR_OPTIONS_HERE)

DEBUG = settings.get('DEBUG', False)
DATABASES = settings.get('DATABASES', {
    'default': {
        'ENGINE': '...',
        'NAME': '...
    }
})
...

# At the end of your settings.py
settings.populate_obj(sys.modules[__name__], ignore=locals())
```

!!! info
    populate_obj accepts a `merge` and `merge_unique` booleans to control
    how merge is performed.
    (added in 3.3.0)

You can still change env with `export DJANGO_ENV=production` and also can export variables like `export DJANGO_DEBUG=true`

!!! note
    Starting in `2.1.1` the `ignore` argument will tell Dynaconf to not override variables that already exist in the current settings file, remove it if you want all the existing local variables to be overwritten by dynaconf.

## Known Caveats

- If `settings.configure()` is called directly it disables Dynaconf, use `settings.DYNACONF.configure()`

## Deprecation note

On old dynaconf releases the solution was to add `dynaconf.contrib.django_dynaconf` to `INSTALLED_APPS` as the first item. This still works but has some limitations so it is not recommended anymore.
