
<img src="https://raw.githubusercontent.com/rochacbruno/dynaconf/master/dynaconf_joystick.png" align="left" width="192px" height="192px"/>
<img align="left" width="0" height="192px" hspace="10"/>

> **dynaconf** - The **dyna**mic **conf**igurator for your Python Project

[![MIT License](https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square)](/LICENSE) [![PyPI](https://img.shields.io/pypi/v/dynaconf.svg)](https://pypi.python.org/pypi/dynaconf) [![PyPI](https://img.shields.io/pypi/pyversions/dynaconf.svg)]() [![Travis CI](http://img.shields.io/travis/rochacbruno/dynaconf.svg)](https://travis-ci.org/rochacbruno/dynaconf) [![Coverage Status](https://coveralls.io/repos/rochacbruno/dynaconf/badge.svg?branch=master&service=github)](https://coveralls.io/github/rochacbruno/dynaconf?branch=master) [![Codacy grade](https://img.shields.io/codacy/grade/5074f5d870a24ddea79def463453545b.svg)](https://www.codacy.com/app/rochacbruno/dynaconf/dashboard)


**dynaconf** is an OSM (**O**bject **S**ettings **M**apper) it can read settings variables from a set of different data stores such as **python settings files**, **environment variables**, **redis**, **memcached**, **ini files**, **json files**, **yaml files** and you can customize **dynaconf** loaders to read from wherever you want. (maybe you really want to read from xml files ughh?)

<br><br>

# Install
```bash
pip install dynaconf
```

> NOTE: this project officially supports and encourages only Python 3+. Currently this is working well and tests are passing on any Python version above 2.7 but at any moment we can drop python2.x support if needed.

# define your settings module

```bash
export DYNACONF_SETTINGS=myproject.settings
or
export DYNACONF_SETTINGS=myproject.production_settings
or
export DYNACONF_SETTINGS=/etc/myprogram/settings.py
```
> HINT: The `DYNACONF_SETTINGS` can be `.py` or `.yml` (Support for json, ini, toml is coming, please contribute.)


> NOTE: If you do not define DYNACONF_SETTINGS so the default will be `settings.py` on the root directory

# you can export extra values

```bash
export DYNACONF_DATABASE='mysql://....'
export DYNACONF_SYSTEM_USER='admin'
export DYNACONF_FOO='bar'
```

Or define all your settings as env_vars starting with **DYNACONF_**

> HINT: You can change `DYNACONF_NAMESPACE` to any name e.g `MYPROJECT` and then environment vars prefixed with `MYPROJECT_` will be loaded.

# Example

```bash
export DYNACONF_SETTINGS=myproject.settings
export DYNACONF_FOO='bar'
export DYANCONF_NUMBER='@int 1234'  # force casting as int when reading
```

### file: myproject/settings.py
```python
NAME = 'Bruno'
```

### file:app.py
```python

from dynaconf import settings

print settings.NAME
print settings.DATABASE
print settings.SYSTEM_USER
print settings.get('FOO')
print settings.NUMBER
```

### then

```bash
python app.py

Bruno
mysql://..
admin
bar
1234
```

# Namespace support

When you are working with multiple projects using the same environment maybe you want to use different namespaces for ENV vars based configs


```bash
export DYNACONF_DATABASE="DYNADB"
export PROJ1_DATABASE="PROJ1DB"
export PROJ2_DATABASE="PROJ2DB"
```

and then access them


```python
from dynaconf import settings

# configure() or configure('settingsmodule.path') is needed
# only when DYNACONF_SETINGS is not defined
settings.configure()

# access default namespace settings
settings.DATABASE
'DYNADB'

# switch namespaces
settings.namespace('PROJ1')
settings.DATABASE
'PROJ1DB'

settings.namespace('PROJ2')
settings.DATABASE
'PROJ2DB'

# return to default, call it without args
settings.namespace()
settings.DATABASE
'DYNADB'
```

You can also use the context manager:

```python
settings.DATABASE
'DYNADB'

with settings.using_namespace('PROJ1'):
    settings.DATABASE
    'PROJ1DB'

with settings.using_namespace('PROJ2'):
    settings.DATABASE
    'PROJ2DB'

settings.DATABASE
'DYNADB'
```

> namespace() and using_namespace() takes optional argument **clean** defaults to True. If you want to keep the pre-loaded values when switching namespaces set it to False.


## Namespaced environment

It is usual to have e.g `production` and `development` environments, the way to set this is:

### Using `settings.py` as base file you just need other `<environment>_settings.py` files.

```bash
settings.py
development_settings.py
production_settings.py
```

Then in your environment.

```bash
export DYNACONF_NAMESPACE=DEVELOPMENT|PRODUCTION  # switch enviroment using env vars.
```

Or using `namespace`

```python

with settings.using_namespace('development'):
    # code here

settings.namespace('development')
```

> NOTE: `settings.py` is the base and `namespace` specific overrides its vars.

### using YAML

Using YAML is easier because it support multiple namespace in one file.

Lets say you have `DYNACONF_NAMESPACE=DYNACONF` (the default)
```yaml
DYNACONF:  # this is the global namespace
  VARIABLE: 'this variable is available on every namespace'
  HOST: null  # this variable is set to None

DEVELOPMENT:
  HOST: devserver.com  # overrides the global or sets new

production:  # upper or lower case does not matter
  host: prodserver.com
```

Then it will be applied using env var `DYNACONF_NAMESPACE` or context manager.

> HINT: When using yaml namespace identifier and first level vars are case
> insensitive, dynaconf will always have them read as upper case.

# casting values from envvars

Sometimes you need to set some values as specific types, boolean, integer, float or lists and dicts.

built in casts

- @int (as_int)
- @bool (as_bool)
- @float (as_float)
- @json (as_json)

> @json / as_json  will use json to load a Python object from string, it is useful to get lists and dictionaries. The return is always a Python object.

strings does not need converters.

You have 2 ways to use the casts.

### Casting on declaration

Just start your ENV settigs with this

```bash
export DYNACONF_DEFAULT_THEME='material'
export DYNACONF_DEBUG='@bool True'
export DYNACONF_DEBUG_TOOLBAR_ENABLED='@bool False'
export DYNACONF_PAGINATION_PER_PAGE='@int 20'
export DYNACONF_MONGODB_SETTINGS='@json {"DB": "quokka_db"}'
export DYNACONF_ALLOWED_EXTENSIONS='@json ["jpg", "png"]'
```

Starting the settings values with @ will make dynaconf.settings to cast it in the time od load.

### Casting on access

```bash
export DYNACONF_USE_SSH='yes'

from dynaconf import settings

```

```python

use_ssh = settings.get('USE_SSH', cast='@bool')
# or
use_ssh = settings('USE_SSH', cast='@bool')
# or
use_ssh = settings.as_bool('USE_SSH')

print use_ssh

True
```

### more examples

```bash
export DYNACONF_USE_SSH='enabled'

export DYNACONF_ALIST='@json [1,2,3]'
export DYNACONF_ADICT='@json {"name": "Bruno"}'
export DYNACONF_AINT='@int 42'
export DYNACONF_ABOOL='@bool on'
export DYNACONF_AFLOAT='@float 42.5'
```

```python

from dynaconf import settings

# original value
settings('USE_SSH')
'enabled'

# cast as bool
settings('USE_SSH', cast='@bool')
True

# also cast as bool
settings.as_bool('USE_SSH')
True

# cast defined in declaration '@bool on'
settings.ABOOL
True

# cast defined in declaration '@json {"name": "Bruno"}'
settings.ADICT
{u'name': u'Bruno'}

# cast defined in declaration '@json [1,2,3]'
settings.ALIST
[1, 2, 3]

# cast defined in decalration '@float 42.5'
settings.AFLOAT
42.5

# cast defined in declaration '@int 42'
settings.AINT
42

```

# Defining default namespace

Include in the file defined in DYNACONF_SETTINGS the desired namespace

```python
DYNACONF_NAMESPACE = 'DYNACONF'
```

# Storing settings in databases

## Using REDIS

Redis support relies on the following two settings that you can setup in the DYNACONF_SETTINGS file


1  Add the configuration for redis client
```python
REDIS_FOR_DYNACONF = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

```

> NOTE: if running on Python 3 include `'decode_responses': True` in `REDIS_FOR_DYNACONF`


Include **redis_loader** in dynaconf LOADERS_FOR_DYNACONF

> the order is the precedence

```python

# Loaders to read namespace based vars from diferent data stores
LOADERS_FOR_DYNACONF = [
    'dynaconf.loaders.env_loader',
    'dynaconf.loaders.redis_loader'
]
```

You can now write variables direct in to a redis hash named `DYNACONF_< NAMESPACE >`

By default **DYNACONF_DYNACONF**


You can also use the redis writer

```python
from dynaconf.utils import redis_writer
from dynaconf import settings

redis_writer.write(settings, name='Bruno', database='localhost', PORT=1234)

```

The above data will be converted to namespaced values and recorded in redis as a hash:

```
DYNACONF_DYNACONF:
    NAME='Bruno'
    DATABASE='localhost'
    PORT='@int 1234'
```

> if you want to skip type casting, write as string intead of PORT=1234 use PORT='1234' as redis stores everything as string anyway

Data is read from redis and another loaders only once or when namespace() and using_namespace() are invoked. You can access the fresh value using **settings.get_fresh(key)**

There is also the **fresh** context manager

```python
from dynaconf import settings

print settings.FOO  # this data was loaded once on import

with settings.fresh():
    print settings.FOO  # this data is being directly read from loaders

```

And you can also force some variables to be **fresh** setting in your setting file

```python
DYNACONF_ALWAYS_FRESH_VARS = ['MYSQL_HOST']
```

or using env vars

```bash
export DYNACONF_ALWAYS_FRESH_VARS='@json ["MYSQL_HOST"]'
```

Then

```python
from dynaconf import settings

print settings.FOO  # This data was loaded once on import

print settings.MYSQL_HOST # This data is being read from redis imediatelly!

```

# Using programatically

Sometimes you want to override settings for your existing Package or Framework
lets say you have a **conf** module exposing a **settings** object and used to do:

`from myprogram.conf import settings`

Now you want to use Dynaconf, open that `conf.py` or `conf/__init__.py` and do:

```python
# coding: utf-8
from dynaconf import LazySettings

settings = LazySettings(
    ENVVAR_FOR_DYNACONF="MYPROGRAM_SETTINGS_MODULE",
    DYNACONF_NAMESPACE='MYPROGRAM'
)

```

Now you can import settings from your own program and dynaconf will do the rest!


# Flask Extension

Dynaconf provides an extension to make your `app.config` in Flask to be a `dynaconf` instance.

```python
from flask import Flask
from dynaconf.contrib import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(
    app,
    ENVVAR_FOR_DYNACONF="MYSITE_SETTINGS_MODULE",
    DYNACONF_NAMESPACE='MYSITE',
    SETTINGS_MODULE_FOR_DYNACONF='settings.yml',  # or settings.py, .toml, .ini etc....
    YAML='.secrets.yml',  # aditional config where you store sensitive data our of vcs
    EXTRA_VALUE='You can add aditional config vars here'
)

```

Take a look at `examples/flask` for more.

> This was inspired by flask.config and django.conf.settings
