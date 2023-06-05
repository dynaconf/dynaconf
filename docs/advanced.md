# advanced usage

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

In the same path of any settings file, you can create a `dynaconf_hooks.py` file
this file will be loaded after all the settings files are loaded.

`dynaconf_hooks.py`
```py

def post(settings):
    data = {"dynaconf_merge": True}
    if settings.DEBUG:
        data["DATABASE_URL"] = "sqlite://"
    return data

```

Dynaconf will execute the `post` function and will merge the returned data with
the existing settings.

To disable the merging of the data, you can set the `dynaconf_merge` to False.

You can also set the merging individually for each settings variable as seen on
[merging](/merging/) documentation.


## `inspect_settings`

> **NEW** in version 3.2.0

Inspect the loading history of all ingested data by its source identities.

This function relates all ingested data to its source by establishing a set of
source metadata on loading-time:

- **loader**: which kind of loader *(yaml, envvar, validation_default)*
- **identifier**: specific identifier *(eg: filename for files)*
- **env**: which env this data belongs to *(global, main, development, etc)*
- **merged**: if this data has been merged *(True or False)*

It also provides key and environment filters to narrow down the results,
descending/ascending sorting flag and some built-in output formats.

Sample usage:

```python
$ export DYNACONF_FOO=from_environ
$ export DYNACONF_BAR=environ_only
$ cat file_a.yaml
foo: from_yaml

$ python
>>> from dynaconf import Dynaconf, inspect_settings
>>> settings = Dynaconf()
>>> inspect_settings(settings, key_dotted_path="foo", output_format="yaml")
header:
  filters:
    env: None
    key: foo
    history_ordering: ascending
  active_value: from_environ
history:
- loader: yaml
  identifier: file_a.yaml
  env: default
  merged: false
  value:
    FOO: from_yaml
- loader: env_global
  identifier: unique
  env: global
  merged: false
  value:
    FOO: from_environ
    BAR: environ_only
```

To save to a file use:

```python
inspect_setting(setting, to_file="filename.json", output_format="json")
```

Dynaconf supports some builtin formats, but you can use a custom dumper too that
can dump nested dict/list structure into a `TextIO` stream.

## Programmatically loading a settings file

You can load files from within a python script.

When using relative paths, it will use `root_path` as its basepath.
Learn more about how `root_path` fallback works [here](/configuration#root_path).

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

    if key:
        value = decrypted_config.get(key.lower())
        obj.set(key, value)
    else:
        obj.update(decrypted_config)

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

It is also possible to pass additional [configuration](/configuration/) variables to `from_env` method.

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

## Exporting

You can generate a file with current configs by calling `dynaconf list -o /path/to/file.ext` see more in [cli](/cli/)

You can also do that programmatically with:

```py
from dynaconf import loaders
from dynaconf import settings
from dynaconf.utils.boxing import DynaBox

# generates a dict with all the keys for `development` env
data = settings.as_dict(env='development')

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
