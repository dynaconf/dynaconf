
<img src="https://raw.githubusercontent.com/rochacbruno/dynaconf/master/dynaconf_joystick.png" align="left" width="192px" height="192px"/>
<img align="left" width="0" height="192px" hspace="10"/>

> **dynaconf** - The **dyna**mic **conf**igurator for your Python Project

[![MIT License](https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square)](/LICENSE) [![PyPI](https://img.shields.io/pypi/v/dynaconf.svg)](https://pypi.python.org/pypi/dynaconf) [![PyPI](https://img.shields.io/pypi/pyversions/dynaconf.svg)]() [![Travis CI](http://img.shields.io/travis/rochacbruno/dynaconf.svg)](https://travis-ci.org/rochacbruno/dynaconf) [![Coverage Status](https://coveralls.io/repos/rochacbruno/dynaconf/badge.svg?branch=master&service=github)](https://coveralls.io/github/rochacbruno/dynaconf?branch=master) [![Codacy grade](https://img.shields.io/codacy/grade/5074f5d870a24ddea79def463453545b.svg)](https://www.codacy.com/app/rochacbruno/dynaconf/dashboard)


**dynaconf** a layered configuration system for Python applications - 
with strong support for [12-factor applications](https://12factor.net/config) 
and extensions for **Flask** and **Django**.

<br><br>

## install Dynaconf in a Python 3 environment

```bash
# to use with settings.py, settings.json, .env or environment vars
pip3 install dynaconf

# to include support for more file formats
pip3 install dynaconf[yaml]
pip3 install dynaconf[toml]
pip3 install dynaconf[ini]
pip3 install dynaconf[redis]
pip3 install dynaconf[vault]

# for a complete installation
pip3 install dynaconf[all]
```

## How does it work?

```python
# import the unique dynaconf object
from dynaconf import settings

# access your config variables
Connect(user=settings.USERNAME, passwd=settings.PASSWD)

# You can provide defaults in case config is missing
Connect(user=settings('USERNAME', 'admin'), passwd=settings('PASSWD', 1234))
```

##  Where the values come from? 

> Dynaconf will look for variables in the following order (by default) and you can also customize the order of loaders.

- Settings files files in the order: `settings.{py|yaml|toml|ini|json}`
- `.env` file
- `export`ed Environment Variables
- Remote storage servers
- Multiple customizable sources

### 12factor recommended example (environment variables):

```bash
# put some variable in a .env file
echo "DYNACONF_USERNAME=admin" >> .env
```

```bash
# Or export directly
export DYNACONF_USERNAME=admin
export DYNACONF_PASSWD='@int 1234'  # you can type the values!
```

Just read it

```python
# import the unique dynaconf object
from dynaconf import settings

# access your config variables
Connect(user=settings.USERNAME, passwd=settings.PASSWD)
```

> NOTE: You can customize the prefix `DYNACONF_` to your own namespace like `MYAPP_USERNAME` exporting `NAMESPACE_FOR_DYNACONF=MYAPP`.

# Features

- Read config variables from unique `dynaconf` object
- Values can come from different sources:
    - Load values from `settings.{py|yaml|toml|ini}` file
    - Load values from `.env` files
    - Load values from System's Exported `Environment Variables`
    - **And even more:**
        - Load values from a remote **Redis** server
        - Load values from a remote **SQL** database
        - Load values from a remote **memcached**
        - Load values from a remote [Secrets Vault](https://www.vaultproject.io/)
    - **And if you want:**
        - Load values from **anywhere** you want, easy to implement your own loader!
- Flexible **typing system**
    - Export Typed environment variables using dynaconf data type markers `export FOO=@int 42`
- **Flask Support**
    - In your Flask application just do `FlaskDynaconf(app)` and then read values from `app.config` object
- **Feature Flag System**
    - Implement a feature flag system using dynaconf as store and checker
- **Value validation**
    - Validate the config variables and define rules

# Examples 

## Choose a file format to store your settings or store it in environment variables

Choose the file format that best fit your project and call it `settings.{py|yaml|toml|ini}` 
put this file in the root directory of your project. If you don't want to have a `settings` file
dynaconf can also read values from environment variables or `.env` files.

### Try it

**0 -** Install `dynaconf` with TOML support

```bash
pip install dynaconf[toml]
```

**1 -** Create a `settings.toml` to store default project settings

```toml
[dynaconf]
server = 'foo.com'
username = 'admin'
password = false
```

**2 -** Create `.secrets.toml` to store sensitive variables

```toml
[dynaconf]
password = 'My5up3r53c4et'
```

**3 -** Create a `.env` to override values in specific environments

```bash
DYNACONF_USERNAME=admin
```

> The `.env` is optional, it also works if `export DYNACONF_VARIABLE=x` is used

**4 -** Create a `.gitignore` to remove `.secrets.*` and `.env` from VCS

```bash
.env
.secrets.*
```

**5 -** Create the `program.py`

```python
from dynaconf import settings

print(settings.USERNAME)
print(settings.SERVER)
print(settings.PASSWORD)
```

**6 -** Run it

```bash
$ python program.py
admin
foo.com
My5up3r53c4et
```

It is possible to have multiple sources at the same time but the **recommendation**
is to pick a single format for your configurations and use envvars or .env to override it.

## Namespace support

When you are working with multiple projects using the same environment maybe you want to use different namespaces for ENV vars based configs


```bash
export DYNACONF_DATABASE="DYNADB"
export PROJ1_DATABASE="PROJ1DB"
export PROJ2_DATABASE="PROJ2DB"
```

and then access them


```python
>>> from dynaconf import settings

# access default namespace settings
>>> settings.DATABASE
'DYNADB'

# switch namespaces
>>> settings.namespace('PROJ1')
>>> settings.DATABASE
'PROJ1DB'

>>> settings.namespace('PROJ2')
>>> settings.DATABASE
'PROJ2DB'

# return to default, call it without args
>>> settings.namespace()
>>> settings.DATABASE
'DYNADB'
```

You can also use the context manager:

```python
>>> settings.DATABASE
'DYNADB'

>>> with settings.using_namespace('PROJ1'):
...    settings.DATABASE
    'PROJ1DB'

>>> with settings.using_namespace('PROJ2'):
...    settings.DATABASE
    'PROJ2DB'

>>> settings.DATABASE
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
export NAMESPACE_FOR_DYNACONF=DEVELOPMENT|PRODUCTION  # switch enviroment using env vars.
```

Or using `namespace`

```python

with settings.using_namespace('development'):
    # code here

settings.namespace('development')
```

> NOTE: `settings.py` is the base and `namespace` specific overrides its vars.

### using YAML

> you need to install with `pip install dynaconf[yaml]`

Just save a `settings.yaml` in the root dir.

Using YAML is easier because it support multiple namespace in a single file.

Lets say you have `NAMESPACE_FOR_DYNACONF=DYNACONF` (the default)
```yaml
DYNACONF:  # this is the global namespace
  VARIABLE: 'this variable is available on every namespace'
  HOST: null  # this variable is set to None

DEVELOPMENT:
  HOST: devserver.com  # overrides the global or sets new

production:  # upper or lower case does not matter
  host: prodserver.com
```

Then it will be applied using env var `NAMESPACE_FOR_DYNACONF` or context manager.

> HINT: When using yaml namespace identifier and first level vars are case
> insensitive, dynaconf will always have them read as upper case.


### using TOML

> you need to install with `pip install dynaconf[toml]`

Just save a `settings.toml` in the root dir.

Using TOML is easier because it support multiple namespace in a single file.

Lets say you have `NAMESPACE_FOR_DYNACONF=DYNACONF` (the default)
```toml
[dynaconf]  # this is the global namespace
variable = 'this variable is available on every namespace'
HOST = false  # this variable is set to False

[DEVELOPMENT]
HOST = 'devserver.com'  # overrides the global or sets new

[production]  # upper or lower case does not matter
host = 'prodserver.com'
```

Then it will be applied using env var `NAMESPACE_FOR_DYNACONF` or context manager.

> HINT: When using toml namespace identifier and first level vars are case
> insensitive, dynaconf will always have them read as upper case.


### using INIFILES

> you need to install dynaconf with `pip install dynaconf[ini]`

Just save a `settings.ini` in the root dir.

Using INI is easier because it support multiple namespace in a single file.

Lets say you have `NAMESPACE_FOR_DYNACONF=DYNACONF` (the default)

```ini
[DYNACONF]
VARIABLE = "this variable is available on every namespace"

[DEVELOPMENT]
HOST = "devserver.com"

[production]
host = "prodserver.com"
```

Then it will be applied using env var `NAMESPACE_FOR_DYNACONF` or context manager.

> HINT: When using INI namespace identifier and first level vars are case
> insensitive, dynaconf will always have them read as upper case.


### using JSON

Just save a `settings.json` in the root dir.

Using JSON is easier because it support multiple namespace in a single file.

Lets say you have `NAMESPACE_FOR_DYNACONF=DYNACONF` (the default)
```json
{
  "DYNACONF": {
    "VARIABLE": "this variable is available on every namespace",
    "HOST": null
  },
  "DEVELOPMENT": {
    "HOST": "devserver.com"
  },
  "production": {
    "host": "prodserver.com"
  }
}
```

Then it will be applied using env var `NAMESPACE_FOR_DYNACONF` or context manager.

> HINT: When using json namespace identifier and first level vars are case
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

Dynaconf uses the `AUTO_CAST` of envvars, just start your ENV vars names with a
typed prefix like in the examples below.

```bash
export DYNACONF_DEFAULT_THEME='material'
export DYNACONF_DEBUG='@bool True'
export DYNACONF_DEBUG_TOOLBAR_ENABLED='@bool False'
export DYNACONF_PAGINATION_PER_PAGE='@int 20'
export DYNACONF_MONGODB_SETTINGS='@json {"DB": "quokka_db"}'
export DYNACONF_ALLOWED_EXTENSIONS='@json ["jpg", "png"]'
```

Starting the settings values with @ will make dynaconf.settings to cast it in the time od load.

There is support for `@int, @float, @bool, @json, @note`

> **NOTE:** To disable the AUTO_CAST you can set a env var `export AUTO_CAST_FOR_DYNACONF=off`

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

Include in the `settings.py` or in the file defined in the envvar DYNACONF_SETTINGS or in the `.env` file or in the customized LazySettings class the desired namespace

```python
NAMESPACE_FOR_DYNACONF = 'MYPROGRAM'
```

# Storing settings in databases

## Using Hashicorp Vault

The https://www.vaultproject.io/ is a key:value store for secrets and Dynaconf can load
variables from a Vault secret.

1. Run a vault server
Run a Vault server installed or via docker:

```bash
docker run -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
```

2. Install support for vault in dynaconf

```bash
pip install dynaconf[vault]
```

3. In your `.env` file or in environment variables do:

```bash
VAULT_FOR_DYNACONF_ENABLED=1
VAULT_FOR_DYNACONF_URL="http://localhost:8200"
VAULT_FOR_DYNACONF_TOKEN="myroot"
VAULT_FOR_DYNACONF_PATH="/secret/data/"   # the resulting namespace will have namespace added as in /secret/data/dynaconf
```

Now you can have keys like `PASSWORD` and `TOKEN` defined in the vault and
dynaconf will read it.

To write a new secret you can use http://localhost:8200 web admin and write keys
under the `/secret/dynaconf` secret database.

You can also use the Dynaconf writer via Python terminal

```python
from dynaconf.loaders.vault_loader import write
write({'password': '123456'})
```

## Using REDIS


1  Add the configuration for redis client
```python
REDIS_FOR_DYNACONF = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True
}
```

> NOTE: if running on Python 3 include `'decode_responses': True` in `REDIS_FOR_DYNACONF`

Enable the loader in `.env` or as environment variable

```bash
REDIS_FOR_DYNACONF_ENABLED=1
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
    NAMESPACE_FOR_DYNACONF='MYPROGRAM'
)

```

Now you can import settings from your own program and dynaconf will do the rest!


# Flask Extension

Dynaconf provides an extension to make your `app.config` in Flask to be a `dynaconf` instance.

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app)
```

Now the `app.config` will read values from `dynaconf.settings`


# Django Extension

Dynaconf provides an extnesion to make `django.conf.settings` to be a dynaconf instance

In your django project's `settings.py` include:

```python
INSTALLED_APPS = [
    'dynaconf.contrib.django_dynaconf',
    ...
]
```

> **NOTE**: The extension must be included as the first INSTALLED_APP of the list

Now create your `settings.{py|yaml|toml|ini|json}` in your project's root directory
(the same folder where `manage.py` is located)

Now when doing `form django.conf import settings` this settings object will read values from dynaconf


## DEBUGGING

By default Dynaconf only outputs the ERROR level to debug it change

```bash
export DEBUG_LEVEL_FOR_DYNACONF='INFO'
```

## The loading precedende order

Dynaconf will perform loads in this order:

1. Load Default configuration
2. Load Environment variables (pre load to read initial DYNACONF_ config)
3. Load Settings file in the order defined in `SETTINGS_MODULE_FOR_DYNACONF` by default will to load `'settings.py,settings.yaml,settings.toml'` in this order overriding previous values
4. Load all loaders defined in `LOADERS_FOR_DYNACONF` by default only `environment variables` will be read again and get higher precedence

The files will be tried to load in the following order allowing overrides

```python
[
 'settings.py', '.secrets.py',
 'settings.yaml', 'settings.yml', '.secrets.yaml', '.secrets.yml',
 'settings.toml', 'settings.tml', '.secrets.toml', '.secrets.tml',
 'settings.ini', 'settings.conf', 'settings.properties',
 '.secrets.ini', '.secrets.conf', '.secrets.properties',
 'settings.json', '.secrets.json'
]
```

## Customizing the loaders

In a setting file like `settings.{py|yaml|toml|ini|json}` define:

```python
LOADERS_FOR_DYNACONF = [
    'dynaconf.loaders.env_loader',
    'dynaconf.loaders.redis_loader',
    'YourCustomLoaderPath'
]
```

export also works

```bash
export LOADERS_FOR_DYNACONF='@json ["loader1", "loader2"]'
```

Loaders will be executed in that order.

To disable loaders do:

```
LOADERS_FOR_DYNACONF=0
```

> This will cause environment variables to lose the higher precedence

## More examples:

Take a look at [example/](/example) for more.

> This was inspired by flask.config and django.conf.settings
