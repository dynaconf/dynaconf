# Advanced Usage

Yeah **Dynamic** is part of the name of this library so you can do lots of things :)

## Customizing the settings object

Sometimes you want to override settings for your existing Package or Framework
lets say you have a **conf** module exposing a **config** object and used to do:

```python
from myprogram.conf import config
```

Now you want to use Dynaconf, open that `conf.py` or `conf/__init__.py` and do:

```python
# coding: utf-8
from dynaconf import LazySettings

config = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF="MYPROGRAM")
```

Now you can use `export MYPROGRAM_FOO=bar` instead of `DYNACONF_FOO=bar`

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

It is also possible to pass additional [configuration](configuration.html) variables to `from_env` method.

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

You can use dynaconf values to populate Python objects (intances).

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

## Customizations

It is possible to customize how your project will load settings, example: You want your users to customize a settings file defined in `export PROJECTNAME_SETTINGS=/path/to/settings.toml` and you want environment variables to be loaded from `PROJECTNAME_VARNAME`


```python
ENVVAR_PREFIX_FOR_DYNACONF = "PROJECTNAME"
"""This defines which environment variable global prefix dynaconf will load
That means that `export PROJECTNAME_FOO=1` will be loaded to `duanconf.settings.FOO
On command line it is possible to check it with `dynaconf list -k foo`"""

ENV_SWITCHER_FOR_DYNACONF='PROJECTNAME_ENV'
"""By default it is ENV_FOR_DYNACONF, this is the envvar used to switch from development to production
but with this settings your users can do `export PROJECT_ENV=production` (new in 2.0.0)"""


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
settings = LazySettings(
    ENVVAR_PREFIX_FOR_DYNACONF=ENVVAR_PREFIX_FOR_DYNACONF,
    ENVVAR_FOR_DYNACONF=ENVVAR_FOR_DYNACONF,
    ENV_SWITCHER_FOR_DYNACONF=ENV_SWITCHER_FOR_DYNACONF
)
```

Then the working environment can now be switched using `export PROJECTNAME_ENV=production`

## Exporting

You can generate a file with current configs by calling `dynaconf list -o /path/to/file.ext` see more in [cli](cli.html)

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
from dynaconf import LazySettings

settings = LazySettings(
  PRELOAD_FOR_DYNACONF=["/path/*", "other/settings.toml"],                # <-- Loaded first
  SETTINGS_FILE_FOR_DYNACONF="/etc/foo/settings.py",                      # <-- Loaded second (the main file)
  INCLUDES_FOR_DYNACONF=["other.module.settings", "other/settings.yaml"]  # <-- Loaded at the end
)

```
