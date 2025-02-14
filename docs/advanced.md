# Advanced Usage

## Hooks

> **NEW** in version 3.1.6

Hooks are useful when you need to conditionally load data that depends on the
previously loaded settings.

Before getting into hooks, lets understand why they are useful.

Imagine your application uses 2 settings modules: `plugin_settings.py` and `settings.py`.

`plugin_settings.py`
```py
DEBUG = True
```

`settings.py`
```py
if DEBUG:
    # do something
```

`app.py`
```py
from dynaconf import Dynaconf
settings = Dynaconf(
    preload=['plugin_settings.py'],
    settings_file="settings.py"
)
```

The above code will fail with NameError: name 'DEBUG' is not defined on settings.py
that happens because `plugin_settings.py` is loaded before `settings.py` but also
before the `app.py` is fully loaded.

### Hooks for the solution

A hook is basically a function that takes an optional read-only `settings`
positional argument and return data to be merged on the Settings object.

There are two ways to add hooks: from special modules or directly in a Dynaconf
instantiation.

#### Module approach

With the module approach, you can create a `dynaconf_hooks.py` file in the same
path as any settings file. Then, the hooks from this module will be loaded
after the regular loading process.

```py
# dynaconf_hooks.py

def post(settings):
    data = {"dynaconf_merge": True}
    if settings.DEBUG:
        data["DATABASE_URL"] = "sqlite://"
    return data

```

Dynaconf will execute the `post` function and will merge the returned data with
the existing settings.

#### Instance approach

With the instance approach, just add your hook function to Dynaconf `post_hook`
initialization argument. It accepts a single `Callable` or a list of `Callable`

```python
def hook_function(settings):
    data = {"dynaconf_merge": True}
    if settings.DEBUG:
        data["DATABASE_URL"] = "sqlite://"
    return data

settings = Dynaconf(post_hooks=hook_function)
```

You can also set the merging individually for each settings variable as seen on
[merging](merging.md) documentation.


#### Decorator approach

**new in 3.2.8**

When the settings file is a Python file, you can also use a decorator to define hooks.

```python
from dynaconf import Dynaconf

settings = Dynaconf(settings_file="settings.py")
```

```python title="settings.py"
from dynaconf import post_hook

VARIABLE = "value"
# all regular settings here
...

@post_hook
def set_debugging_database_url(settings):
    data = {}
    if settings.DEBUG:
        data["DATABASE_URL"] = "sqlite://"
    return data
```

Dynaconf will collect the decorated functions and execute them after the settings file is loaded.

The hook decorator can only be applied to functions that are defined withing the same settings file, in the
need to use external functions, wrap it in a local decorated function.

When using `load_file` to load a python file, hooks will also be collected and immediately executed after the file is loaded, unless the `run_hooks` argument is set to `False`, this is useful when calling `load_file` multiple times and have the hooks to be all executed together at a certain point later.

`execute_instance_hooks` helper method is also available to trigger execution of collected hooks, but usually not
needed because a common pattern is to call the latest `load_file` with `run_hooks=True` to trigger all hooks at once.

Notice that load_file will execute all collected hooks that have not been called yet, it does not execute hooks that have already been called (unless the hook itself is marked as `_called=False`). This is useful when you want to reload a file and re-execute hooks.

## Inspecting History

> **NEW** in version 3.2.0

!!! warning
    This feature is in **tech preview** the usage interface and output format is
    subject to change.

This feature purpose is to allow tracking any config-data loading history, that is, the loading steps that lead to a given final value. It can return a dict data report, print to `stdout` or write to a file, and is also available as a [CLI command](cli.md#dynaconf-inspect-tech-preview).

It works by setting a *SourceMetadata* object to every ingested data, so it can be recovered and filtered to generate meaningful reports. The properties of this object are:

- **loader**: the loader type *(e.g, yaml, envvar, validation_default)*
- **identifier**: specific identifier *(e.g, filename for files)*
- **env**: which environ this data belongs to *(global, main, development, etc)*
- **merged**: if this data has been merged *(True or False)*

Dynaconf offers two very similar utility functions to get data from it: `inspect_settings` and `get_history`. The difference is that `get_history` returns a simple list of dict-records with source metadata, while `inspect_settings` focus on generating a printable report (and thus it offers some convenience options for that).

They are available at `dynaconf.inspect_settings` and `dynaconf.get_history`

### `inspect_settings`

By default, it only returns a dict-report. You can optionally print the report in a specific format, such as "yaml" or "json", or write it to a file:

```python
# default: returns python object
>>> inspect_settings(settings_obj)
{
	"header": ... # filtering options used
	"current": ... # currently active data/value
	"history": ... # list of history records
}

# print report
>>> inspect_settings(setting_obj, print_report=True, dumper="yaml")
header:
  - ...
current:
  - ...
history:
  - ...

# write to file
>>> inspect_settings(settings_obj, to_file="report.yaml", dumper="json")
```

The history looks like this:

```python
>>> inspect_settings(
>>> 	settings_obj,
>>> 	key="foo",
>>> 	print_report=True,
>>> 	dumper="yaml"
>>> )
>>>

header:
- ...
current:
- ...
history:
- loader: env_global
  identifier: unique
  env: global
  merged: false
  value: FOO
- loader: toml
  identifier: path/to/file.yaml
  env: development
  merged: false
  value: FOO
```

<h4>Options Overview</h4>

There are some pre-defined ways that you can filter and customize the report.
Here is a summary of the available argument options:

Positional:

- `settings` (required): A Dynaconf instance
- `key`: Filter by this key. E.g "path.to.key"
- `env`: Filter by this env. E.g "production"

Kwargs-only:

- `new_first`: If True, uses newest to oldest loading order.
- `history_limit`: Limits how many entries are shown. By default, show all.
- `include_internal`: If True, include internal loaders (e.g. defaults). This has effect only if key is not provided.
- `to_file`: If specified, write dumped report to this filename.
- `print_report`: If true, prints the dumped report to stdout.
- `dumper`: Accepts preset strings (e.g. "yaml", "json") or custom dumper callable ``(dict, TextIO) -> None``. If not provided, does nothing.
- `report_builder`: If provided, it is used to generate the report dict.

### `get_history`

Returns a list of history-records (the same as in the `history` key of `inspect_settings` records. In fact, `inspect_settings` uses `get_history`, so this is just available if your main goal is to use the data directly. It offer some basic filtering capabilities, but it is assumed that if you choose to use this you'll probably want to process and filter the data by your own.


### `get_debug_info`

Returns a dictionary containing debug information about the settings object. This information includes the current environment, the settings file, the loaders, and the history of the settings object.

```python
from dynaconf.utils.inspect_settings import get_debug_info
get_debug_info(settings.DYNACONF, verbosity=0, key="data")
# result
{'core_loaders': [],
 'environments': ['development', 'production'],
 'history': [{'data': {}, 'identifier': 'init_kwargs', 'loader': 'set_method'},
             {'data': {},
              'identifier': 'default_settings',
              'loader': 'set_method'},
             {'data': {},
              'identifier': 'envvars_first_load',
              'loader': 'set_method'},
             {'data': {},
              'identifier': 'settings_module_method',
              'loader': 'set_method'},
             {'data': {'data': [0]},
              'identifier': '/etc/app/defaults.py',
              'loader': 'py'},
             {'data': {'data': '@merge 7,8,9'},
              'identifier': '/etc/app/settings.yaml',
              'loader': 'yaml'},
 'loaded_envs': ["development"],
 'loaded_files': ['/etc/app/defaults.py',
                  '/etc/app/settings.yaml'],
 'loaded_hooks': [],
 'post_hooks': [],
 'root_path': '/run/app',
 'validators': [],
 'versions': {'django': '4.2.16', 'dynaconf': '3.2.8.dev0'}}
```


## Update dynaconf settings using command-line arguments (cli)

Dynaconf is designed to load the settings file and, when applicable, prioritize overrides from envvar.

The following examples demonstrate the process of incorporating command-line arguments to update the Dynaconf settings, ensuring that the CLI input takes precedence over both the settings.toml file and environment variables.

### Command-line arguments using argparse

This illustration showcases the utilization of Python's `argparse` module to exemplify the creation of a command-line interface (CLI) capable of overriding the settings.toml file and environment variables.

`app.py`
```py
from __future__ import annotations

from dynaconf import settings

import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Simple argparse example for overwrite dynaconf settings"
    )

    parser.add_argument("--env", default=settings.current_env)
    parser.add_argument("--host", default=settings.HOST)
    parser.add_argument("--port", default=settings.PORT)

    options, args = parser.parse_known_args(argv)

    # change the environment to update proper settings
    settings.setenv(options.env)

    # update the dynaconfig settings
    settings.update(vars(options))

    #

if __name__ == "__main__":
    main(argv=None)
```


### Command-line arguments using click

This illustration showcases the utilization of Python's `click` module to exemplify the creation of a command-line interface (CLI) capable of overriding the settings.toml file and environment variables.

`app.py`
```py
from __future__ import annotations

from dynaconf import settings

import click


@click.command()
@click.option("--host", default=settings.HOST, help="Host")
@click.option("--port", default=settings.PORT, help="Port")
@click.option("--env", default=settings.current_env, help="Env")
def app(host, port, env):
    """Simple click example for overwrite dynaconf settings"""

    # change the environment to update proper settings
    settings.setenv(env)

    # update the dynaconfig settings
    settings.update({"host": host, "port": port})

if __name__ == "__main__":
    app()
```

Alternatively you can use a more generic approach using `**options` and passing `options` to dynaconf

`app.py`
```py
from __future__ import annotations

from dynaconf import settings

import click


@click.command()
@click.option("--host", default=settings.HOST, help="Host")
@click.option("--port", default=settings.PORT, help="Port")
@click.option("--env", default=settings.current_env, help="Env")
def app(**options):
    """Simple click example for overwrite dynaconf settings"""

    # change the environment to update proper settings
    settings.setenv(options['env'])

    # update the dynaconfig settings
    settings.update(options)

if __name__ == "__main__":
    app()
```

## Programmatically loading a settings file

You can load files from within a python script.

When using relative paths, it will use `root_path` as its basepath.
Learn more about how `root_path` fallback works [here](configuration.md#root_path).

```python
from dynaconf import Dynaconf

settings = Dynaconf()

# single file
settings.load_file(path="/path/to/file.toml")

# list
settings.load_file(path=["/path/to/file.toml", "/path/to/another-file.toml"])

# separated by ; or ,
settings.load_file(path="/path/to/file.toml;/path/to/another-file.toml")
```

Notice that data loaded by this method is not persisted.

Once `env` is changed via `setenv|using_env`, `reload` or `configure` invocation, its loaded data
will be cleaned. To persist consider using `INCLUDES_FOR_DYNACONF` variable or assuring it will
be loaded programmatically again.

**new in 3.2.7**

- Calls to `load_file` will be recorded on the inspect history and include module and line number.


## Prefix filtering

```toml
[production]
PREFIX_VAR = TEST
OTHER = FOO
```

```py
from dynaconf import Dynaconf
from dynaconf.strategies.filtering import PrefixFilter

settings = Dynaconf(
    settings_file="settings.toml",
    environments=False,
    filter_strategy=PrefixFilter("prefix")
)
```

Loads only vars prefixed with `prefix_`

## Creating new loaders

In your project i.e called `myprogram` create your custom loader.

`myprogram/my_custom_loader.py`

```python
def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "obj" a single key or all keys from source
    :param obj: the settings instance
    :param env: settings current env (upper case) default='DEVELOPMENT'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all from `env`
    :param filename: Custom filename to load (useful for tests)
    :return: None
    """
    # Load data from your custom data source (file, database, memory etc)
    # use `obj.set(key, value)` or `obj.update(dict)` to load data
    # use `obj.find_file('filename.ext')` to find the file in search tree
    # Return nothing
```

In the `.env` file or exporting the envvar define:

```bash
LOADERS_FOR_DYNACONF=['myprogram.my_custom_loader', 'dynaconf.loaders.env_loader']
```

Dynaconf will import your `myprogram.my_custom_loader.load` and call it.

> **IMPORTANT**: the `'dynaconf.loaders.env_loader'` must be the last in the loaders list
> if you want to keep the behavior of having envvars to override parameters.

In case you need to disable all external loaders and rely only the `settings.*` file loaders define:

```bash
LOADERS_FOR_DYNACONF=false
```

In case you need to disable all core loaders and rely only on external loaders:

```bash
CORE_LOADERS_FOR_DYNACONF='[]'  # a toml empty list
```


For example, if you want to add a [SOPS](https://github.com/mozilla/sops) loader

```py
def load(
    obj: LazySettings,
    env: str = "DEVELOPMENT",
    silent: bool = True,
    key: str = None,
    filename: str = None,
) -> None:
    sops_filename = f"secrets.{env}.yaml"
    sops_file = obj.find_file(sops_filename)
    if not sops_file:
        logger.error(f"{sops_filename} not found! Secrets not loaded!")
        return

    _output = run(["sops", "-d", sops_file], capture_output=True)
    if _output.stderr:
        logger.warning(f"SOPS error: {_output.stderr}")
    decrypted_config = yaml.load(_output.stdout, Loader=yaml.CLoader)

    # support for inspecting
    source_metadata = SourceMetadata('sops', sops_file, env)

    if key:
        value = decrypted_config.get(key.lower())
        obj.set(key, value, loader_identifier=source_metadata)
    else:
        obj.update(decrypted_config, loader_identifier=source_metadata)

    obj._loaded_files.append(sops_file)
```

See more [tests_functional/custom_loader](https://github.com/dynaconf/dynaconf/tree/master/tests_functional/custom_loader)

## Module impersonation

In some cases you may need to impersonate your legacy `settings` module for example you already have a program that does.

```python
from myprogram import settings
```

and now you want to use dynaconf without the need to change your whole codebase.

Go to your `myprogram/settings.py` and apply the module impersonation.

```python
import sys
from dynaconf import LazySettings

sys.modules[__name__] = LazySettings()
```

the last line of above code will make the module to replace itself with a dynaconf instance in the first time it is imported.

## Switching working environments

You can switch between existing environments using:

- `from_env`: (**recommended**) Will create a new settings instance pointing to defined env.
- `setenv`: Will set the existing instance to defined env.
- `using_env`: Context manager that will have defined env only inside its scope.

### from_env

> **New in 2.1.0**

Return a new isolated settings object pointing to specified env.

Example of settings.toml::

```ini
[development]
message = 'This is in dev'
foo = 1
[other]
message = 'this is in other env'
bar = 2
```

Program::

```py
>>> from dynaconf import settings
>>> print(settings.MESSAGE)
'This is in dev'
>>> print(settings.FOO)
1
>>> print(settings.BAR)
AttributeError: settings object has no attribute 'BAR'
```

Then you can use `from_env`:

```py
>>> print(settings.from_env('other').MESSAGE)
'This is in other env'
>>> print(settings.from_env('other').BAR)
2
>>> print(settings.from_env('other').FOO)
AttributeError: settings object has no attribute 'FOO'
```

The existing `settings` object remains the same.

```py
>>> print(settings.MESSAGE)
'This is in dev'
```

You can assign new settings objects to different `envs` like:

```py
development_settings = settings.from_env('development')
other_settings = settings.from_env('other')
```

And you can choose if the variables from different `envs` will be chained and overridden in a sequence:

```py
all_settings = settings.from_env('development', keep=True).from_env('other', keep=True)

>>> print(all_settings.MESSAGE)
'This is in other env'
>>> print(all_settings.FOO)
1
>>> print(all_settings.BAR)
2
```

The variables from [development] are loaded keeping pre-loaded values, then the variables from [other] are loaded keeping pre-loaded from [development] and overriding it.

It is also possible to pass additional [configuration](configuration.md) variables to `from_env` method.

```py
new_settings = settings.from_env('production', keep=True, SETTINGS_FILE_FOR_DYNACONF='another_file_path.yaml')
```

Then the `new_settings` will inherit all the variables from existing env and also load the `another_file_path.yaml` production env.

### setenv

Will change `in_place` the `env` for the existing object.

```python
from dynaconf import settings

settings.setenv('other')
# now values comes from [other] section of config
assert settings.MESSAGE == 'This is in other env'

settings.setenv()
# now working env are back to previous
```

### using_env

Using context manager

```python
from dynaconf import settings

with settings.using_env('other'):
    # now values comes from [other] section of config
    assert settings.MESSAGE == 'This is in other env'

# existing settings back to normal after the context manager scope
assert settings.MESSAGE == 'This is in dev'
```

## Populating objects

> **New in 2.0.0**

You can use dynaconf values to populate Python objects (instances).

example:
```py
class Obj:
   ...
```

then you can do:

```py
from dynaconf import settings  # assume it has DEBUG=True and VALUE=42.1
obj = Obj()

settings.populate_obj(obj)

assert obj.DEBUG is True
assert obj.VALUE == 42.1

```

Also you can specify only some keys:

```py
from dynaconf import settings  # assume it has DEBUG=True and VALUE=42.1
obj = Obj()

settings.populate_obj(obj, keys=['DEBUG'])

assert obj.DEBUG is True  # ok

assert obj.VALUE == 42.1  # AttributeError

```

**new in 3.2.7**
- `populate_obj` will take `internals` boolean to enable or disable populating internal settings.


**new in 3.2.8**

- `populate_obj` will take `convert_to_dict` boolean to enable or disable converting the settings object to a dict before populating the object, this makes the data structures like Box and BoxList to be converted to the raw dict/list before populating the object.


## Exporting

You can generate a file with current configs by calling `dynaconf list -o /path/to/file.ext` see more in [cli](cli.md)

You can also do that programmatically with:

```py
from dynaconf import loaders
from dynaconf import settings
from dynaconf.utils.boxing import DynaBox

# generates a dict with all the keys for `development` env
data = settings.to_dict(env='development')

# writes to a file, the format is inferred by extension
# can be .yaml, .toml, .ini, .json, .py
loaders.write('/path/to/file.yaml', DynaBox(data).to_dict(), merge=False, env='development')
```

## Preloading files

> New in **2.2.0**

Useful for plugin based apps.

```py
from dynaconf import Dynaconf

settings = Dynaconf(
  preload=["/path/*", "other/settings.toml"],                # <-- Loaded first
  settings_file="/etc/foo/settings.py",                      # <-- Loaded second (the main file)
  includes=["other.module.settings", "other/settings.yaml"]  # <-- Loaded at the end
)

```


## Testing

For testing it is recommended to just switch to `testing` environment and read the same config files.

`settings.toml`
```toml
[default]
value = "On Default"

[testing]
value = "On Testing"
```

`program.py`
```python
from dynaconf import settings

print(settings.VALUE)
```

```bash
ENV_FOR_DYNACONF=testing python program.py
```

Then your `program.py` will print `"On Testing"` red from `[testing]` environment.


### Pytest

For pytest it is common to create fixtures to provide pre-configured settings object or to configure the settings before
all the tests are collected.

Examples available on [https://github.com/dynaconf/dynaconf/tree/master/tests_functional/pytest_example](https://github.com/dynaconf/dynaconf/tree/master/tests_functional/pytest_example)

With `pytest` fixtures it is recommended to use the `FORCE_ENV_FOR_DYNACONF` instead of just `ENV_FOR_DYNACONF` because it has precedence.

#### Configure Dynaconf with Pytest

Define your `root_path`

```py
import os

from dynaconf import Dynaconf

current_directory = os.path.dirname(os.path.realpath(__file__))

settings = Dynaconf(
    root_path=current_directory, # defining root_path
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
)
```

#### A python program

`settings.toml` with the `[testing]` environment.

```toml
[default]
VALUE = "On Default"

[testing]
VALUE = "On Testing"
```

`app.py` that reads that value from current environment.
```py
from dynaconf import settings


def return_a_value():
    return settings.VALUE
```

`tests/conftest.py` with a fixture to force `settings` to run pointing to `[testing]` environment.

```py
import pytest
from dynaconf import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
```

`tests/test_dynaconf.py` to assert that the correct environment is loaded

```py
from app import return_a_value


def test_dynaconf_is_in_testing_env():
    assert return_a_value() == "On Testing"
```

#### A Flask program

`settings.toml` with the `[testing]` environment.

```toml
[default]
VALUE = "On Default"

[testing]
VALUE = "On Testing"
```

`src.py` that has a Flask application factory

```py
from flask import Flask
from dynaconf.contrib import FlaskDynaconf


def create_app(**config):
    app = Flask(__name__)
    FlaskDynaconf(app, **config)
    return app

```

`tests/conftest.py` with a fixture to provide `app` dependency injection to all the tests,
And force this `app` to point to `[testing]` config environment.

```py
import pytest
from src import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app(FORCE_ENV_FOR_DYNACONF="testing")
    return app
```

`tests/test_flask_dynaconf.py` to assert that the correct environment is loaded

```py
def test_dynaconf_is_on_testing_env(app):
    assert app.config["VALUE"] == "On Testing"
    assert app.config.current_env == "testing"
```

### Mocking

But it is common in unit tests to `mock` some objects and you may need in rare cases to mock the `dynaconf.settings` when running your tests.

```python
from dynaconf.utils import DynaconfDict
mocked_settings = DynaconfDict({'FOO': 'BAR'})
```

DynaconfDict is a dict like obj that can be populated from a file:

```python
from dynaconf.loaders import toml_loader
toml_loader.load(mocked_settings, filename='my_file.toml', env='testing')
```
