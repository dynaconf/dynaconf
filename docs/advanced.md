# advanced usage

## Programmatically loading a settings file

```python
from dynaconf import settings
settings.load_file(path="/path/to/file.toml")  # list or `;/,` separated allowed
```

> **NOTE**: programmatically loaded file is not persisted, once `env` is changed via `setenv|ugin_env`, or a `reload` or `configure` is invoked it will be cleaned, to persist it needs to go to `INCLUDES_FOR_DYNACONF` variable or you need to load it programmatically again.


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

See more [example/custom_loader](https://github.com/rochacbruno/dynaconf/tree/master/example/custom_loader)

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

Examples available on [https://github.com/rochacbruno/dynaconf/tree/master/example/pytest_example](https://github.com/rochacbruno/dynaconf/tree/master/example/pytest_example)

With `pytest` fixtures it is recommended to use the `FORCE_ENV_FOR_DYNACONF` instead of just `ENV_FOR_DYNACONF` because it has precedence.

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
