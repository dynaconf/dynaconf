# Getting Started

## Installation

> Python 3.x is required

```
$ pip install dynaconf
```

> Default installation supports .toml, .py and .json file formats and also environment variables (.env supported) - to support YAML add `pip install dynaconf[yaml]` or `pip install dynaconf[all]`

## Usage

### Accessing config variables in your Python application

In your Python program wherever you need to access a settings variable you use the canonical object `from dynaconf import settings`:

#### Example of program to connect to some database

```python
from some.db import Client

from dynaconf import settings

conn = Client(
    username=settings.USERNAME,             # attribute style access
    password=settings.get('PASSWORD'),      # dict get style access
    port=settings['PORT'],                  # dict item style access
    timeout=settings.as_int('TIMEOUT'),     # Forcing casting if needed
    host=settings.get('HOST', 'localhost')  # Providing defaults
)
```

### Where the settings values are stored

Dynaconf aims to have a flexible and usable configuration system. Your applications can be configured via a **configuration files**, through **environment variables**, or both. Configurations are separated into environments: **[development], [staging], [testing] and [production]**. The working environment is selected via an environment variable.

**Sensitive data** like tokens, secret keys and password can be stored in `.secrets.*` files and/or external storages like `Redis` or `vault` secrets server.

Besides the built-in optional support to **redis** as settings storage dynaconf allows you to create **custom loaders** and store the data wherever you want e.g: databases, memory storages, other file formats, nosql databases etc.

## Working environments

At any point in time, your application is operating in a given configuration environment. By default there are four such environments:

- [development]
- [staging]
- [testing]
- [production]

> You can also define **[custom environment]** and use the pseudo-envs **[default]** to provide comprehensive default values and **[global]** to provide global values to overrride in any other environment.

Without any action, your applications by default run in the **[development]** environment. The environment can be changed via the `ENV_FOR_DYNACONF` environment variable. For example, to launch an application in the **[staging]** environment, we can run:

```bash
export ENV_FOR_DYNACONF=staging
```

or

```bash
ENV_FOR_DYNACONF=staging python yourapp.py
```

> **NOTE:** When using [FLask Extension](flask.html) the environment can be changed via `FLASK_ENV` variable and for [Django Extension](django.html) you can use `DJANGO_ENV`.

## The settings files

> IMPORTANT: Dynaconf by default reads settings files using `utf-8` encoding, if you have settings files written in other encoding please set `ENCODING_FOR_DYNACONF` environment variable see more in [configuration](configuration.html)

An optional `settings.{toml|py|json|ini|yaml}` file can be used to specify the configuration parameters for each environment. If it is not present, only the values from **environment variables** are used (**.env** file is also supported). Dynaconf searches for the file starting at the current working directory. If it is not found there, Dynaconf checks the parent directory. Dynaconf continues checking parent directories until the root is reached.

The recommended file format is **TOML** but you can choose to use any of **.{toml|py|json|ini|yaml}**.

The file must be a series of sections, at least one for **[default]**, optionally one for each **[environment]**, and an optional **[global]** section. Each section contains **key-value** pairs corresponding to configuration parameters for that **[environment]**. If a configuration parameter is missing, the value from **[default]** is used. The following is a complete `settings.toml` file, where every standard configuration parameter is specified within the **[default]** section:

> **NOTE**: if the file format choosen is `.py` as it does not support sections you can create multiple files like `settings.py` for [default], `development_settings.py`, `production_settings.py` and `global_settings.py`. **ATTENTION**: using `.py` is not recommended for configuration - use **TOML**!

```ini
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

```ini
[global]
address = "1.2.3.4"

[development]
address = "localhost"

[production]
address = "0.0.0.0"
```

> **NOTE**: The **[env]** name and first level variables are case insensitive as internally dynaconf will always use upper case, that means **[development]** and **[DEVELOPMENT]** are equivalent and **address** and **ADDRESS** are also equivalent. **But the recommendation is to `always use lower case in files` and `always use upper case in env vars and .py files`** (This rule does not apply for inner data structures as dictionaries and arrays).

## Supported file formats

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

> **NOTE**: Dynaconf works in an **layered override** mode based on the above order, so if you have multiple file formats with conflicting keys defined, the precedence will be based on the loading order.

Take a look at the [example](https://github.com/rochacbruno/dynaconf/tree/master/example) folder to see some examples of use with different file formats.
