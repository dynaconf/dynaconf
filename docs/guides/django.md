# Django Extension

Dynaconf extensions for Django works by patching the `settings.py` file with dynaconf loading hooks, the change is done on a single file and then in your whole project every time you call `django.conf.settings` you will have access to `dynaconf` attributes and methods.

Ensure dynaconf is installed on your env `pip install dynaconf[yaml]`

## Initialize the extension

You can manually append at the bottom of your django project's `settings.py` the following code:

```python
# HERE STARTS DYNACONF EXTENSION LOAD
# Important! Keep it at the very bottom of your Django's settings.py file
import os, sys, dynaconf  # noqa
dynaconf.default_settings.AUTO_LOAD_DOTENV = False  # noqa
dynaconf.default_settings.start_dotenv(root_path=os.path.dirname(os.path.abspath(__file__)))  # noqa
settings = dynaconf.DjangoDynaconf(sys.modules[__name__])  # noqa
# Important! No more code below this line
# HERE ENDS DYNACONF EXTENSION LOAD
```

Or optionally you can, on the same directory where your `manage.py` is located run:

```bash
export DJANGO_SETTINGS_MODULE=yourapp.settings
$ dynaconf init

# or passing the location of the settings file

$ dynaconf init --django yourapp/settings.py

```

Dynaconf will append its extension loading code to the bottom of your `yourapp/settings.py` file and will create `settings.toml` and `.secrets.toml` in the current folder (the same where `manage.py` is located).

## Using `DJANGO_` environment variables

Then **django.conf.settings** will work as a `dynaconf.settings` instance and `DJANGO_` will be the global prefix to export environment variables.

Example:

```bash
export DJANGO_DEBUG=true     # django.conf.settings.DEBUG
export DJANGO_INTVALUE=1     # django.conf.settings['INTVALUE]
export DJANGO_HELLO="Hello"  # django.conf.settings.get('HELLO)
```

## Settings files

You can also have settings files for your Django app, in the root directory (the same where `manage.py` is located) put your `settings.{yaml, toml, ini, json, py}` and `.secrets.{yaml, toml, ini, json, py}` files and then define your environments `[default]`, `[development]` and `[production]`.

> NOTE: **.yaml** is the recommended format for Django applications because it allows complex data structures in easy way, but feel free to choose any format you are familiar with.

To switch the working environment the `DJANGO_ENV` variable can be used, so `DJANGO_ENV=development` to work
in development mode or `DJANGO_ENV=production` to switch to production.

> **IMPORTANT**: To use `$ dynaconf` CLI the `DJANGO_SETTINGS_MODULE` environment variable must be defined.

IF you don't want to manually create your config files take a look at the [CLI](cli.html)

## Customizations

It is possible to customize how your django project will load settings, example: You want your users to customize a settings file defined in `export PROJECTNAME_SETTINGS=/path/to/settings.toml` and you want environment variables to be loaded from `PROJECTNAME_VARNAME`

Edit django `settings.py` and modify the dynaconf extension part:

from:

```python
# HERE STARTS DYNACONF EXTENSION LOAD
...
settings = dynaconf.DjangoDynaconf(sys.modules[__name__])
# Important! No more code below this line
# HERE ENDS DYNACONF EXTENSION LOAD
```

to:

```python
# HERE STARTS DYNACONF EXTENSION LOAD
...
settings = dynaconf.DjangoDynaconf(
    sys.modules[__name__]
    GLOBAL_ENV_FOR_DYNACONF='PROJECTNAME',
    ENV_FOR_DYNACONF=os.environ.get('PROJECTNAME_ENV', 'DEVELOPMENT'),
    SETTINGS_MODULE_FOR_DYNACONF='/etc/projectname/settings.toml',
    ENVVAR_FOR_DYNACONF='PROJECTNAME_SETTINGS',
    INCLUDES_FOR_DYNACONF=['/etc/projectname/plugins/*'],
)
# Important! No more code below this line
# HERE ENDS DYNACONF EXTENSION LOAD
```

 Variables on environment can be set/override using `PROJECTNAME_` prefix e.g: `export PROJECTNAME_DEBUG=true`.

Working environment can now be switched using `export PROJECTNAME_ENV=production` it defaults to `development`.

Your settings are now read from `/etc/projectname/settings.toml` (dynaconf will not perform search for all the settings formats). This settings location can be changed via envvar using `export PROJECTNAME_SETTINGS=/other/path/to/settings.py{yaml,toml,json,ini}`

You can have additional settings read from `/etc/projectname/plugins/*` any supoprted file from this folder will be loaded.

You can set more options, take a look on [configuration](configuration.html)

## Deprecation note

On old dynaconf releases the solution was to add `dynaconf.contrib.django_dynaconf` to `INSTALLED_APPS` as the first item, this still works but has some limitations so it is not recommended anymore.
