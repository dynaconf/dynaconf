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

config = LazySettings(GLOBAL_ENV_FOR_DYNACONF="MYPROGRAM")
```

Now you can use `export MYPROGRAM_FOO=bar` instead of ~~DYNACONF_FOO=bar~~

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
