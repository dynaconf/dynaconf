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

## Switching working environments

To switch the `environment` programatically you can use `setenv` or `using_env`.

Using context manager

```python
from dynaconf import settings

with settings.using_env('envname'):
    # now values comes from [envmane] section of config
    assert settings.HOST == 'host.com
```

Using env setter

```python
from dynaconf import settings

settings.setenv('envname')
# now values comes from [envmane] section of config
assert settings.HOST == 'host.com'

settings.setenv()
# now working env are back to previous
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
"""By default it is DYNACONF_ENV, this is the envvar used to switch from development to production
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
    ENVVAR_FOR_DYNACONF=ENVVAR_FOR_DYNACONF.
    ENV_SWITCHER_FOR_DYNACONF=ENV_SWITCHER_FOR_DYNACONF
)
```

Then the working environment can now be switched using `export PROJECTNAME_ENV=production`
