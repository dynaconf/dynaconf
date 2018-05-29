```
██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝
```

> **dynaconf** - The **dyna**mic **conf**igurator for your Python Project

[![MIT License](https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square)](/LICENSE) [![PyPI](https://img.shields.io/pypi/v/dynaconf.svg)](https://pypi.python.org/pypi/dynaconf) [![PyPI](https://img.shields.io/pypi/pyversions/dynaconf.svg)]() [![Travis CI](http://img.shields.io/travis/rochacbruno/dynaconf.svg)](https://travis-ci.org/rochacbruno/dynaconf) [![codecov](https://codecov.io/gh/rochacbruno/dynaconf/branch/master/graph/badge.svg)](https://codecov.io/gh/rochacbruno/dynaconf) [![Codacy grade](https://img.shields.io/codacy/grade/5074f5d870a24ddea79def463453545b.svg)](https://www.codacy.com/app/rochacbruno/dynaconf/dashboard)

**dynaconf** a layered configuration system for Python applications -
with strong support for [12-factor applications](https://12factor.net/config)
and extensions for **Flask** and **Django**.

**Documentation**: http://dynaconf.readthedocs.io/

# Features

- Strict separation of settings from code (following [12-factor applications](https://12factor.net/config) Guide).
- Define comprehensive default values.
- Store parameters in multiple file formats (**.toml**, .json, .yaml, .ini and .py).
- Sensitive **secrets** like tokens and passwords can be stored in safe places like `.secrets` file or `vault server`.
- Parameters can optionally be stored in external services like Redis server.
- Simple **feature flag** system.
- Layered **[environment]** system.
- Environment variables can be used to override parameters.
- Support for `.env` files to automate the export of environment variables.
- Correct data types (even for environment variables).
- Have **only one** canonical settings module to rule all your instances.
- Drop in extension for **Flask** `app.config` object.
- Drop in extension for **Django** `conf.settings` object.
- Powerful **$ dynaconf** CLI to help you manage your settings via console.
- Customizable **Validation** System to ensure correct config parameters.
- Allow the change of **dyna**mic parameters on the fly without the need to redeploy your application.

## install Dynaconf

> Python 3.x is required

```bash
# Default installation supports .toml, .py and .json file formats
# and also overriding from environment variables (.env supported)
$ pip3 install dynaconf
```

## Getting Started

### Accessing config variables in your Python application

In your Python program wherever you need to access a settings variable you use the canonical object `from dynaconf import settings`:

#### Example of program to connect to some database

```python
from some.db import Client
from dynaconf import settings  # import `dynaconf.settings` canonical settings object

conn = Client(
    username=settings.USERNAME,             # attribute style access
    password=settings.get('PASSWORD'),      # dict get style access
    port=settings['PORT'],                  # dict item style access
    timeout=settings.as_int('TIMEOUT'),     # Forcing casting if needed
    host=settings.get('HOST', 'localhost')  # Providing defaults if key is not defined
)
```

### Where the settings values are stored

Dynaconf aims to have a flexible and usable configuration system. Your applications can be configured via a **configuration files**, through **environment variables**, or both. Configurations are separated into environments: **[development], [staging], [testing] and [production]**. The working environment is selected via an environment variable.

**Sensitive data** like tokens, secret keys and password can be stored in `.secrets.*` files and/or external storages like `Redis` or `vault` secrets server.

Besides the built-in optional support to **redis** as settings storage dynaconf allows you to create **custom loaders** and store the data wherever you want e.g: databases, memory storages, other file formats, nosql databases etc.

### environments

At any point in time, your application is operating in a given configuration environment. By default there are four such environments:

- [development]
- [staging]
- [testing]
- [production]

> You can also define **[custom environment]** and use the pseudo-envs **[default]** to provide comprehensive default values and **[global]** to provide global values to overrride in any other environment.

Without any action, your applications by default run in the **[development]** environment. The environment can be changed via the `ÈNV_FOR_DYNACONF` environment variable. For example, to launch an application in the **[staging]** environment, we can run:

```bash
export ENV_FOR_DYNACONF=staging
```

or

```bash
ENV_FOR_DYNACONF=staging python yourapp.py
```

## The settings files

An optional `settings.{toml|py|json|ini|yaml}` file can be used to specify the configuration parameters for each environment. If it is not present, only the values from **environment variables** are used (**.env** file is also supported). Dynaconf searches for the file starting at the current working directory. If it is not found there, Dynaconf checks the parent directory. Dynaconf continues checking parent directories until the root is reached.

The recommended file format is **TOML** but you can choose to use any of **.{toml|py|json|ini|yaml}**.

The file must be a series of sections, at most one for **[default]**, optionally one for each **[environment]**, and an optional **[global]** section. Each section contains **key-value** pairs corresponding to configuration parameters for that **[environment]**. If a configuration parameter is missing, the value from **[default]** is used. The following is a complete `settings.toml` file, where every standard configuration parameter is specified within the **[default]** section:

> **NOTE**: if the file format choosen is `.py` as it does not support sections you can create multiple files like `settings.py` for [default], `development_settings.py`, `production_settings.py` and `global_settings.py`. **ATTENTION** using `.py` is not recommended for configuration use **TOML**!


```toml
[default]
username = "admin"
port = 5000
host = "localhost"
message = "default message"
value = "default value"

[development]
username = "devuser"

[staging]
host = "staging.server.com"

[testing]
host = "testing.server.com"

[production]
host = "server.com"

[awesomeenv]
value = "this value is set for custom [awesomeenv]"

[global]
message = "This value overrides message of default and other envs"
```

The **[global]** pseudo-environment can be used to set and/or override configuration parameters globally. A parameter defined in a **[global]** section sets, or overrides if already present, that parameter in every environment. For example, given the following `settings.toml` file, the value of address will be **"1.2.3.4"** in every environment:

```toml
[global]
address = "1.2.3.4"

[development]
address = "localhost"

[production]
address = "0.0.0.0"
```

> **NOTE**: The **[env]** name and first level variables are case insensitive as internally dynaconf will always use upper case, that means **[development]** and **[DEVELOPMENT]** are equivalent and **address** and **ADDRESS** are also equivalent. This rule does not apply for inner data structures as dictionaries and arrays.

### Settings file supported formats

By default **toml** is the recommended format to store your configuration, however you can switch to a different supported format.

```bash
# If you wish to include support for more sources
pip3 install dynaconf[yaml|ini|redis|vault]

# for a complete installation
pip3 install dynaconf[all]
```

Once the support is installed no extra configuration is needed to load data from those files, dynaconf will search for settings files in
the root directory of your application looking for the following files in the exact order below:

```python
DYNACONF_LOADING_ORDER = [
 'settings.py',
 '.secrets.py',
 'settings.toml',
 '.secrets.toml',
 'settings.yaml',
 '.secrets.yaml',
 'settings.ini',
 '.secrets.ini',
 'settings.json',
 '.secrets.json',
 # redis server if REDIS_ENABLED_FOR_DYNACONF=true
 # vault server if VAULT_ENABLED_FOR_DYNACONF=true
 # other sources if custom loaders are defined
 # All environment variables prefixed with DYNACONF_
]
```

> **NOTE:** Dynaconf works in an **layered override** mode based on the above order, so if you have multiple file formats with conflicting keys defined, the precedence will be based on the loading order.

Take a look at the [example](/example) folder to see some examples of use with different file formats.

## Storing sensitive secrets

To safely store sensitive data Dynaconf also searches for a `.secrets.{toml|py|json|ini|yaml}` file to look for data like tokens and passwords.

example `.secrets.toml`:

```toml
[default]
password = "sek@987342$"
```

The secrets file supports all the **environment** definitions supported in the **settings** file.

> **IMPORTANT**: The reason to use a `.secrets.*` file is the ability to omit this file when commiting to the repository so a recommended `.gitignore` should include `.secrets.*` line.

## Scafolding

Dynaconf provides a **CLI** to easily configure your application configuration, once dynaconf is installed go to the root directory of your application and run:

```bash
# creates settings files in current directory
$ dynaconf init -v key=value -v otherkey=othervalue -s token=1234 -e production
```

The above command will create in the current directory

`settings.toml`

```toml
[default]
KEY = "default"
OTHERKEY = "default"

[production]
KEY = "value"
OTHERKEY = "othervalue"
```

also `.secrets.toml`

```toml
[default]
TOKEN = "default"

[production]
TOKEN = "1234"
```

The command will also create a `.env` setting the working environment to **[production]**

```bash
ENV_FOR_DYNACONF="PRODUCTION"
```

And will include the `.secrets.toml` in the `.gitignore`

```conf
# Ignore dynaconf secret files
.secrets.*
```

> **NOTE**: refer to the documentation to see more **CLI** commands to manage your configuration files such as **dynaconf list** and **dynaconf write**

**For sensitive data in production is recommended using http://vaultproject.io as dynaconf supports reading and writing values to vault servers, see `vault loader` documentation**

## Environment variables

All configuration parameters, including **custom** envs and ***_FOR_DYNACONF** settings, can be overridden through environment variables. To override the configuration parameter **{param}**, use an environment variable named **DYNACONF_{PARAM}**. For instance, to override the **"host"** configuration parameter, you can run your application with:

```bash
DYNACONF_HOST=other.com python yourapp.py
```

### .env files

If you don't want to declare the variables on every program call you can `export DYNACONF_*` variables or put the values in `.env` files located in the same directory as your settings files.

### Configuration FOR_DYNACONF

The **DYNACONF_** prefix is set by **GLOBAL_ENV_FOR_DYNACONF** and serves only to be used in environment variables to override config values.

This prefix itself can be changed to something more significant for your application, however we recommend kepping **DYNACONF_** as your global env prefix.

> **NOTE**: See the `Configuring Dynaconf` section in documentation to learn more on how to use `.env` variables to configure dynaconf behavior.

### Environment variables precedence and casting

Environment variables take precedence over all other configuration sources: if the variable is set, it will be used as the value for the parameter. Variable values are parsed as if they were **TOML** syntax. As illustration, consider the following examples:

```bash
DYNACONF_INTEGER=42
DYNACONF_FLOAT=3.14
DYNACONF_STRING=Hello
DYNACONF_STRING="Hello"

# booleans
DYNACONF_BOOL=true
DYNACONF_BOOL=false

# Use extra quotes to force a string from other type
DYNACONF_STRING="'42'"
DYNACONF_STRING="'true'"

# Arrays must be homogenous in toml syntax
DYNACONF_ARRAY=[1, 2, 3]
DYNACONF_ARRAY=[1.1, 2.2, 3.3]
DYNACONF_ARRAY=['a', 'b', 'c']
DYNACONF_DICT={key="abc",val=123}

# toml syntax does not allow `None/null` values so use @none
DYNACONF_NONE='@none None'

# toml syntax does not allow mixed type arrays so use @json
DYNACONF_ARRAY='@json [42, 3.14, "hello", true, ["otherarray"], {"foo": "bar"}]'
```

> **NOTE**: Older versions of Dynaconf used the `@casting` prefixes for env vars like `export DYNACONF_INTEGER='@int 123'` still works but this casting is deprecated in favor of using TOML syntax described above. To disable the `@casting` do `export AUTO_CAST_FOR_DYNACONF=false`

#### Boxed values

In Dynaconf values are Boxed, it means the dot notation can also be used to access dictionary members, example:

settings.toml

```toml
[default]
mysql = {host="server.com", port=3600, auth={user="admin", passwd=1234}}
```

You can now access

```python
from dynaconf import settings

connect(
    host=settings.MYSQL.host,
    port=settings.MYSQL.port,
    username=settings.MYSQL.auth.user,
    passwd=settings.MYSQL.auth.get('passwd'),
)
```

# External storages

## Using Hashicorp Vault to store secrets

The https://www.vaultproject.io/ is a key:value store for secrets and Dynaconf can load
variables from a Vault secret.

1. Run a vault server

Run a Vault server installed or via docker:

```bash
$ docker run -d -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
```

2. Install support for vault in dynaconf

```bash
$ pip install dynaconf[vault]
```

3. In your `.env` file or in exported environment variables define:

```bash
VAULT_ENABLED_FOR_DYNACONF=true
VAULT_URL_FOR_DYNACONF="http://localhost:8200"
VAULT_TOKEN_FOR_DYNACONF="myroot"
```

Now you can have keys like `PASSWORD` and `TOKEN` defined in the vault and
dynaconf will read it.

To write a new secret you can use http://localhost:8200 web admin and write keys
under the `/secret/dynaconf` secret database.

You can also use the Dynaconf writer via console

```bash
$ dynaconf write vault -s password=123456
```

## Using REDIS

1. Run a Redis server installed or via docker:

```bash
$ docker run -d -p 6379:6379 redis
```

2. Install support for redis in dynaconf

```bash
$ pip install dynaconf[redis]
```

3. In your `.env` file or in exported environment variables define:

```bash
REDIS_ENABLED_FOR_DYNACONF=true
REDIS_HOST_FOR_DYNACONF=localhost
REDIS_PORT_FOR_DYNACONF=6379
```

You can now write variables direct in to a redis hash named `DYNACONF_< env >`

You can also use the redis writer

```bash
$ dynaconf write redis -v name=Bruno -v database=localhost -v port=1234
```

The above data will be recorded in redis as a hash:

```
DYNACONF_DYNACONF {
    NAME='Bruno'
    DATABASE='localhost'
    PORT='@int 1234'
}
```

> if you want to skip type casting, write as string intead of PORT=1234 use PORT="'1234'".

Data is read from redis and another loaders only once when `dynaconf.settings` is first accessed
or when `.setenv()` or `using_env()` are invoked.

You can access the fresh value using **settings.get_fresh(key)**

There is also the **fresh** context manager

```python
from dynaconf import settings

print(settings.FOO)  # this data was loaded once on import

with settings.fresh():
    print(settings.FOO)  # this data is being freshly reloaded from source
```

And you can also force some variables to be **fresh** setting in your setting file

```python
FRESH_VARS_FOR_DYNACONF = ['MYSQL_HOST']
```

or using env vars

```bash
export FRESH_VARS_FOR_DYNACONF='["MYSQL_HOST", "OTHERVAR"]'
```

Then

```python
from dynaconf import settings

print(settings.FOO)         # This data was loaded once on import

print(settings.MYSQL_HOST)  # This data is being read from redis imediatelly!
```

# Using programatically

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


## Feature flag system (feature toggles)

Feature flagging is a system to dynamically toggle features in your
application based in some settings value.

Learn more at: https://martinfowler.com/articles/feature-toggles.html

Example:

write flags to redis
```
$ dynaconf write redis -s NEWDASHBOARD=1 -e premiumuser
```

meaning: Any premium user has NEWDASHBOARD feature enabled!

In your program do:

```python
usertype = 'premiumuser'  # assume you loaded it from your database

# user has access to new dashboard?
if settings.flag('newdashboard', usertype):
    activate_new_dashboard()
else:
    # User will have old dashboard if not a premiumuser
    activate_old_dashboard()
```

The value is ensured to be loaded fresh from redis server so features can be enabled or 
disabled at any time without the need to redeploy.

It also works with file settings but the recommended is redis
as the data can be loaded once it is updated.


# Framework Extensions

## Flask Extension

Dynaconf providesa drop in replacement for `app.config` 
This an extension makes your `app.config` in Flask to be a `dynaconf` instance.

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app)
```

Now the `app.config` will work as a `dynaconf.settings` and **FLASK_** will be the
global prefix for exporting environment variables.

```bash
export FLASK_DEBUG=true
export FLASK_INTVALUE=1
```

The working environment will also respect the `FLASK_ENV` variable, so `FLASK_ENV=development` to work 
in development mode or `FLASK_ENV=production` to switch to production.

> **NOTE**: To use `$ dynaconf` CLI the `FLASK_APP` must be defined.


## Django Extension

Dynaconf a drop in replacement to `django.conf.settings` 
This an extension makes your `app.config` in Flask to be a `dynaconf` instance.


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

Now **django.conf.settings** will work as a `dynaconf.settings` instance and **DJANGO_** will
be the global prefix to export environment variables.

```bash
export DJANGO_DEBUG=true
export DJANGO_INTVALUE=1
```

It is recommended that all the **django's** internal config vars should be kept
in the `settings.py` of your project, then application specific values your can 
place in dynaconf's `settings.toml` in the root (same folder as manage.py).
You can override settings.py values in the dynaconf settings file.

> **NOTE**: To use `$ dynaconf` CLI the `DJANGO_SETTINGS_MODULE` must be defined and the cli must be called
> from the same directory where manage.py is placed.

## DEBUGGING

By default Dynaconf only outputs the `ERROR` level of logs and you can change it:

```bash
export DEBUG_LEVEL_FOR_DYNACONF=DEBUG
```

## Customizing the loaders

In your project i.e called `myprogram` create your custom loader.

`myprogram/my_custom_loader.py`

```python
def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "obj" a single key or all keys from source
    :param obj: the settings instance
    :param env: settings current env default='development'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :param filename: Custom filename to load
    :return: None
    """
    # Load data from your custom data source (file, database, memory etc)
    # use `obj.set` or `obj.update` to include the data in dynaconf
```

In the `.env` file or exporting the envvar define:

```bash
LOADERS_FOR_DYNACONF=['myprogram.my_custom_loader', 'dynaconf.loaders.env_loader']
```

Dynaconf will import your `myprogram.my_custom_loader.load` and call it.

> **IMPORTANT**: the `'dynaconf.loaders.env_loader'` must be the last in the loaders list
> if you want to keep the behavior of having envvars to override parameters.

In case you need to disable all external loaders and ue only the `settings.*` file loaders define:

```bash
LOADERS_FOR_DYNACONF=false
```

## Testing and mocking

For testing it is recommended to just switch to `testing` environment and read the same config files.
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

## Validation

Dynaconf allows the validation of settings parameters, in some cases you may want to validate the settings before starting the program.

Lets say you have `settings.toml`

```toml
[default]
version = "1.0.0"
age = 35
name = "Bruno"

[production]
PROJECT = "This is not hello_world"
```

At any point of your program you can do:

```python
from dynaconf import settings, Validator

# Register validators
settings.validators.register(
    # Ensure some parameters exists (are required)
    Validator('VERSION', 'AGE', 'NAME', must_exist=True),

    # Ensure some password cannot exist
    Validator('PASSWORD', must_exist=False),

    # Ensure some parameter mets a condition
    # conditions: (eq, ne, lt, gt, lte, gte, identity, is_type_of, is_in, is_not_in)
    Validator('AGE', lte=30, gte=10),

    # validate a value is eq in specific env
    Validator('PROJECT', eq='hello_world', env='production'),
)

# Fire the validator
settings.validators.validate()
```

The above will raise `dynaconf.validators.ValidationError("AGE must be lte=30 but it is 35 in env DEVELOPMENT")` and `dynaconf.validators.ValidationError("PROJECT must be eq='hello_world' but it is 'This is not hello_world' in env PRODUCTION")`

### Using dynaconf_validators.toml

> **NEW in 1.0.1**

Starting on version 1.0.1 it is possible to define validators in **TOML** file called **dynaconf_validators.toml** placed in the same fodler as your settings files.

`dynaconf_validators.toml` equivalent to program above

```toml
[default]

version = {must_exist=true}
name = {must_exist=true}
password = {must_exist=false}

  [default.age]
  must_exist = true
  lte = 30
  gte = 10

[production]
project = {eq="hello_world"}
```

Then to fire the validation use:

```bash
$ dynaconf validate
```

## The dynaconf CLI

The `$ dynaconf` cli provides some useful commands

```bash
Usage: dynaconf [OPTIONS] COMMAND [ARGS]...

  Dynaconf - Command Line Interface

Options:
  --version  Show dynaconf version
  --docs     Open documentation in browser
  --help     Show this message and exit.

Commands:
  banner    Shows dynaconf awesome banner
  init      Inits a dynaconf project By default it...
  list      Lists all defined config values
  write     Writes data to specific source
  validate  Validates based on dynaconf_validators.toml file
```

## More examples

Take a look at [example/](/example) for more.

## Credits

- Dynaconf is inspired by `flask.config` and `django.conf.settings`
- Some ideas also taken from Rust `config` crate
- Environments definitions ideas taken from Rust `rocket` framework

## Alternatives

Dynaconf tries to define standard and good practices for config and aims to have flexibility and 100% of test coverage for Python 3.x.

Dynaconf implements the best parts of the alternatives below, to implement Dynaconf lots of configuration libraties have been tested and studied.

But if you are still looking for something different take a look at the following excellent alternatives.

- [Python Decouple](https://github.com/henriquebastos/python-decouple)
- [PrettyConf](https://github.com/osantana/prettyconf)
- [Profig](https://bitbucket.org/dhagrow/profig)
- [Everett](https://github.com/willkg/everett)
- [Configman](https://configman.readthedocs.io/en/latest/)
- [PyMLconf](https://pypi.org/project/pymlconf/)
- [AnyConfig](https://github.com/ssato/python-anyconfig)
- [Config](https://pypi.org/project/config/)
- [Conman](https://github.com/the-gigi/conman)

```
██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝
```
