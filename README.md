```
██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝
```

> **dynaconf** - The **dyna**mic **conf**igurator for your Python Project

[![MIT License](https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square)](/LICENSE) [![PyPI](https://img.shields.io/pypi/v/dynaconf.svg)](https://pypi.python.org/pypi/dynaconf) [![PyPI](https://img.shields.io/pypi/pyversions/dynaconf.svg)]() [![Travis CI](http://img.shields.io/travis/rochacbruno/dynaconf.svg)](https://travis-ci.org/rochacbruno/dynaconf) [![Coverage Status](https://coveralls.io/repos/rochacbruno/dynaconf/badge.svg?branch=master&service=github)](https://coveralls.io/github/rochacbruno/dynaconf?branch=master) [![Codacy grade](https://img.shields.io/codacy/grade/5074f5d870a24ddea79def463453545b.svg)](https://www.codacy.com/app/rochacbruno/dynaconf/dashboard)


**dynaconf** a layered configuration system for Python applications - 
with strong support for [12-factor applications](https://12factor.net/config) 
and extensions for **Flask** and **Django**.

<br><br>

## install Dynaconf
> Python 3.x is required

```bash
# Default installation supports .py, .toml, .json file formats
# and also reading from environment variables (.env supported)
pip3 install dynaconf
```

## Getting Started


### Accessing config variables in your Python application

In your Python program wherever you need to access a settings variable do:

```python
# Example of program to connect to some database
from someorm import connect
from dynaconf import settings  # import `dynaconf.settings` canonical settings object

con = connect(
    username=settings.USERNAME,             # attribute style access
    password=settings.get('PASSWORD'),      # dict get style access
    port=settings['PORT'],                  # dict item style access
    timeout=settings.as_int('TIMEOUT'),     # Forcing casting if needed
    host=settings.get('HOST', 'localhost')  # Providing defaults if key not defined
)
```

### Where the settings values are stored?

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

```toml
[default]
username = "admin"
port = 5000
host = "localhost"
message = "default message"

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
[
 'settings.py', '.secrets.py',
 'settings.toml', 'settings.tml', '.secrets.toml', '.secrets.tml',
 'settings.yaml', 'settings.yml', '.secrets.yaml', '.secrets.yml',
 'settings.ini', 'settings.conf', 'settings.properties',
 '.secrets.ini', '.secrets.conf', '.secrets.properties',
 'settings.json', '.secrets.json',
 # redis server if REDIS_FOR_DYNACONF_ENABLED=true
 # vault server if VAULT_FOR_DYNACONF_ENABLED=true
 # All environment variables prefixed with DYNACONF_
]
```

> **NOTE:** Dynaconf works in an **override** mode based on the above order, so if you have multiple file formats with conflicting keys defined, the precedence will be based on the loading order.

## Storing sensitive secrets

To safely store sensitive data Dynaconf also searches for a `.secrets.{toml|py|json|ini|yaml}` file to look for data like tokens and passwords.

example `.secrets.toml:

```toml
[default]
password = "sek@987342$"
```

The secrets file supports all the **environment** definitions supported in the **settings** file.

> **IMPORTANT**: The reason to use a `.secrets.*` file is the ability to omit this file when commiting to the repository so a recommended `.gitignore` should include `.secrets.*` line. 

## Scafolding

Dynaconf provides a **CLI** to easily configure your application configuration, once dynaconf is installed go to the root directory of your application and run:

```bash
dynaconf init -v key=value -v otherkey=othervalue -s token=1234 -e production
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
DYNACONF_INTEGER=1
DYNACONF_FLOAT=3.14
DYNACONF_STRING=Hello
# Use extra quotes to force a string from other type
DYNACONF_STRING="'42'"
DYNACONF_STRING="'true'"
DYNACONF_STRING="Hello"
# booleans
DYNACONF_BOOL=true
DYNACONF_BOOL=false
# Arrays must be homogenous in toml syntax
DYNACONF_ARRAY=[1, 2, 3]
DYNACONF_ARRAY=[1.1, 2.2, 3.3]
DYNACONF_ARRAY=['a', 'b', 'c']
DYNACONF_DICT={key="abc",val=123}
# toml syntax does not allow `None/null` values so use
DYNACONF_NONE='@none None'
```

> **NOTE**: Older versions of Dynaconf used the casting prefixes for env vars like `export DYNACONF_INTEGER='@int 123'` still works but this casting is deprecated in favor of using TOML syntax described above. To disable the `@type` casting `export AUTO_CAST_FOR_DYNACONF=false`
