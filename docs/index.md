# **Dynaconf**

<p align="center">
  <a href="https://dynaconf.com"><img src="img/logo_400.svg?sanitize=true" alt="Dynaconf"></a>
</p>
<p align="center">
    <em>Configuration Management for Python.</em>
</p>

<p align="center"><a href="/LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square"></a> <a href="https://pypi.python.org/pypi/dynaconf"><img alt="PyPI" src="https://img.shields.io/pypi/v/dynaconf.svg"></a> <img alt="Azure DevOps builds (branch)" src="https://img.shields.io/azure-devops/build/rochacbruno/3e08a9d6-ea7f-43d7-9584-96152e542071/1/master.svg?label=windows%20build&amp;logo=windows"> <img alt="Azure DevOps builds (branch)" src="https://img.shields.io/azure-devops/build/rochacbruno/3e08a9d6-ea7f-43d7-9584-96152e542071/1/master.svg?label=linux%20build&amp;logo=linux"> <img alt="Azure DevOps builds (branch)" src="https://img.shields.io/azure-devops/build/rochacbruno/3e08a9d6-ea7f-43d7-9584-96152e542071/1/master.svg?label=macos%20build&amp;logo=apple"> <a href="https://codecov.io/gh/rochacbruno/dynaconf"><img alt="codecov" src="https://codecov.io/gh/rochacbruno/dynaconf/branch/master/graph/badge.svg"></a> <a href="https://www.codacy.com/app/rochacbruno/dynaconf?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rochacbruno/dynaconf&amp;utm_campaign=Badge_Grade"><img alt="Codacy Badge" src="https://api.codacy.com/project/badge/Grade/5074f5d870a24ddea79def463453545b"></a> <img alt="GitHub Release Date" src="https://img.shields.io/github/release-date/rochacbruno/dynaconf.svg"> <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/rochacbruno/dynaconf.svg"> <a href="https://t.me/dynaconf"><img alt="Telegram" src="https://img.shields.io/badge/chat-t.me/dynaconf-blue.svg?logo=telegram"></a></p>

## Features

- Inspired by the **[12-factor application guide](https://12factor.net/config)**
- **Settings management** (default values, validation, parsing, templating)
- Protection of **sensitive information** (passwords/tokens)
- Multiple **file formats** `toml|yaml|json|ini|py` and also customizable loaders.
- Full support for **environment variables** to override existing settings (dotenv support included).
- Optional layered system for **multi environments** `[default, development, testing, production]`
- Built-in support for **Hashicorp Vault** and **Redis** as settings and secrets storage.
- Built-in extensions for **Django** and **Flask** web frameworks.
- **CLI** for common operations such as `init, list, write, validate, export`.

## Quick start

### Install

```bash
pip install dynaconf
```

### Initialize Dynaconf on project

<details markdown="1">
<summary>Using <code>Python Only</code>...</summary>

<h4>Use dynaconf CLI to initialize</h4>

In your project's root directory run `dynaconf init` command.

```bash hl_lines="2"
cd path/to/your/project/
dynaconf init -f toml
```

```plain

⚙️  Configuring your Dynaconf environment
------------------------------------------
🐍 The file `config.py` was generated.

🎛️  settings.toml created to hold your settings.

🔑 .secrets.toml created to hold your secrets.

🙈 the .secrets.* is also included in `.gitignore`
  beware to not push your secrets to a public repo.

🎉 Dynaconf is configured! read more on https://dynaconf.com
```

!!! tip
    You can select `toml|yaml|json|ini|py` on `dynaconf init -f <fileformat>`  **toml** is the default and also the most recommended format for configuration.

<h3> Dynaconf init creates the following files</h3>

```plain
.
├── config.py       # Where you import your settings object (required)
├── .secrets.toml   # Sensitive data like passwords and tokens (optional)
└── settings.toml   # Application setttings (optional)
```

On the file `config.py` Dynaconf init generates the following boilerpate

```python
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.yaml', '.secrets.yaml'],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load this files in the order.
```

!!! tip
    You can create the files yourself instead of using the `init` command as shown above and you can give any name you want instead of the default `config.py` (the file must be in your importable python path) - See more options that you can pass to `Dynaconf` class initializer on https://dynaconf.com

</details>

<details markdown="1">
<summary>Or using <code>Flask</code>...</summary>

<h4>Use FlaskDynaconf extension</h4>

In your Flask project import `FlaskDynaconf` and initialize as a Flask extension.

```python hl_lines="2 6"
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)

FlaskDynaconf(app, settings_files=["settings.toml"])
```

given the setup above your `app.config` is now replaced by a dynaconf instance and you can use it normally.

You can export environment variables.
```bash
export FLASK_NAME=BRUNO
export FLASK_DEBUG=true
```

You can also have a `settings.toml` file in your root directory as specified
in `settings_files` argument.

```toml
[default]
SQLALCHEMY_DB_URI = "sqlite://data.db"
```

!!! info
    On Flask and Django settings files are layered in multiple environments by default, you can
    disable it passing `environments=False` to FlaskDynaconf extension.


And then in your Flask application you can access all the variables.

```python
app.config.NAME == "BRUNO"
app.config['DEBUG'] is True
app.config.SQLALCHEMY_DB_URI == "sqlite://data.db"
```

Dynaconf can also load your Flask extensions for you see more details in [Flask Extension](extensions/flask)

</details>

<details markdown="1">
<summary>Or using <code>Django</code>...</summary>

Ensure you have `DJANGO_SETTINGS_MODULE` exported:

```bash
export DJANGO_SETTINGS_MODULE=yourproject.settings
```

On the same folder where your `manage.py` is located run `dynaconf init` command.

```bash
dynaconf init -f yaml --django
```

Then follow the instructions on terminal.

```plain
Django app detected
⚙️  Configuring your Dynaconf environment
------------------------------------------
🎛️  settings.yaml created to hold your settings.

🔑 .secrets.yaml created to hold your secrets.

🙈 the .secrets.yaml is also included in `.gitignore` 
  beware to not push your secrets to a public repo 
  or use dynaconf builtin support for Vault Servers.

⁉  path/to/yourproject/settings.py is found do you want to add dynaconf? [y/N]: 
```

Answer **y**

```plain
🎠  Now your Django settings are managed by Dynaconf
🎉  Dynaconf is configured! read more on https://dynaconf.com 
```

You can export environments variables using `DJANGO_` prefix.

```bash
export DJANGO_ALLOWED_HOSTS="['*']"
```

Or you can put your configurations only on `settings.yaml` file.

!!! tip
    YAML is the recommended file format for Django

```yaml
development:
    debug: true
```

!!! info
    On Flask and Django settings files are layered in multiple environments by default, you can
    disable it passing `environments=False` to FlaskDynaconf extension.

More details in [Django Extension](extensions/django)

</details>

### Using Dynaconf

Put your settings on `settings.{toml|yaml|ini|json|py}`

```toml
username = "admin"
port = 5555
database = {name='mydb', schema='main'}
```

Put sensitive information on `.secrets.{toml|yaml|ini|json|py}`

```toml
password = "secret123"
```

!!! info
    `dynaconf init` command puts the `.secrets.*` in yout `.gitignore` to avoid it to be exposed on public repos but it is your responsibility to keep it safe in your local environment, also the recommendation for production environments is to use the built-in support for Hashicorp Vault service for password and tokens.

Optionally you can now use environment variables to override values per execution or per environment.

```bash
# override `port` from settings.toml file and automatically casts as `int` value.
export DYNACONF_PORT=9900
```

On your code import the `settings` object

```py
from path.to.project.config import settings

# Reading the settings

settings.username == "admin"  # dot notation with multi nesting support
settings.PORT == 9900  # case insensitive
settings['password'] == "secret123"  # dict like access
settings.get("nonexisting", "default value")  # Default values just like a dict
settings.databases.name == "mydb"  # Nested key traversing
settings['databases.schema'] == "main"  # Nested key traversing

```

## Dependencies

### Vendored

Dynaconf core has no dependency it is using vendored copies of external
libraries such as **python-box, click, python-dotenv, ruamel-yaml, python-toml**

### Optional dependencies

To use external services such as **Redis** and ***Hashicorp Vault** it is necessary
to install additional dependencies using extra deps.

**Vault**

```bash
pip install dynaconf[vault]
```

**Redis**

```bash
pip install dynaconf[redis]
```

## License

This project is licensed under the terms of the MIT license.
