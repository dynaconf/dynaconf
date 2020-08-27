[![Dynaconf](docs/img/logo_400.svg?sanitize=true)](http://dynaconf.com)

> **dynaconf** - Configuration Management for Python.

[![MIT License](https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square)](/LICENSE) [![PyPI](https://img.shields.io/pypi/v/dynaconf.svg)](https://pypi.python.org/pypi/dynaconf) [![PyPI](https://img.shields.io/pypi/pyversions/dynaconf.svg)]() ![PyPI - Downloads](https://img.shields.io/pypi/dm/dynaconf.svg?label=pip%20installs&logo=python) [![Build Status](https://dev.azure.com/rochacbruno/dynaconf/_apis/build/status/rochacbruno.dynaconf?branchName=master)](https://dev.azure.com/rochacbruno/dynaconf/_build/latest?definitionId=1&branchName=master) ![Azure DevOps builds (branch)](https://img.shields.io/azure-devops/build/rochacbruno/3e08a9d6-ea7f-43d7-9584-96152e542071/1/master.svg?label=windows%20build&logo=windows) ![Azure DevOps builds (branch)](https://img.shields.io/azure-devops/build/rochacbruno/3e08a9d6-ea7f-43d7-9584-96152e542071/1/master.svg?label=linux%20build&logo=linux) [![codecov](https://codecov.io/gh/rochacbruno/dynaconf/branch/master/graph/badge.svg)](https://codecov.io/gh/rochacbruno/dynaconf) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/5074f5d870a24ddea79def463453545b)](https://www.codacy.com/app/rochacbruno/dynaconf?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rochacbruno/dynaconf&amp;utm_campaign=Badge_Grade) ![GitHub issues](https://img.shields.io/github/issues/rochacbruno/dynaconf.svg) ![GitHub stars](https://img.shields.io/github/stars/rochacbruno/dynaconf.svg) ![GitHub Release Date](https://img.shields.io/github/release-date/rochacbruno/dynaconf.svg) ![GitHub commits since latest release](https://img.shields.io/github/commits-since/rochacbruno/dynaconf/latest.svg) ![GitHub last commit](https://img.shields.io/github/last-commit/rochacbruno/dynaconf.svg) [![Code Style Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black/) [![Telegram](https://img.shields.io/badge/chat-t.me/dynaconf-blue.svg?logo=telegram)](https://t.me/dynaconf)

## Features

- Inspired by the [12-factor application guide](https://12factor.net/config)
- Settings management (default values, validation, parsing, templating)
- Protection of sensitive information (passwords/tokens)
- Multiple file formats `toml|yaml|json|ini|py` and also customizable loaders.
- Full support for environment variables to override existing settings (dotenv support included).
- Optional layered system for multi environments `[default, development, testing, production]`
- Built-in support for Hashicorp Vault and Redis as settings and secrets storage.
- Built-in extensions for **Django** and **Flask** web frameworks.
- CLI for common operations such as `init, list, write, validate, export`.
- full docs on https://dynaconf.com

## Quick start

### Install

```bash
$ pip install dynaconf
```

#### Initialize Dynaconf on project root directory

```plain
$ cd path/to/your/project/

$ dynaconf init -f toml

⚙️  Configuring your Dynaconf environment
------------------------------------------
🐍 The file `config.py` was generated.

🎛️  settings.toml created to hold your settings.

🔑 .secrets.toml created to hold your secrets.

🙈 the .secrets.* is also included in `.gitignore`
  beware to not push your secrets to a public repo.

🎉 Dynaconf is configured! read more on https://dynaconf.com
```

> **TIP:** You can select `toml|yaml|json|ini|py` on `dynaconf init -f <fileformat>`  **toml** is the default and also the most recommended format for configuration.

#### Dynaconf init creates the following files

```plain
.
├── config.py       # This is from where you import your settings object (required)
├── .secrets.toml   # This is to hold sensitive data like passwords and tokens (optional)
└── settings.toml   # This is to hold your application setttings (optional)
```

On the file `config.py` Dynaconf init generates the following boilerpate

```py
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",  # export envvars with `export DYNACONF_FOO=bar`.
    settings_files=['settings.yaml', '.secrets.yaml'],  # Load files in the given order.
)
```

> **TIP:** You can create the files yourself instead of using the `init` command as shown above and you can give any name you want instead of the default `config.py` (the file must be in your importable python path) - See more options that you can pass to `Dynaconf` class initializer on https://dynaconf.com


#### Using Dynaconf

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

> **IMPORTANT:** `dynaconf init` command puts the `.secrets.*` in your `.gitignore` to avoid it to be exposed on public repos but it is your responsibility to keep it safe in your local environment, also the recommendation for production environments is to use the built-in support for Hashicorp Vault service for password and tokens.


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

## More

- Settings Schema Validation
- Custom Settings Loaders
- Vault Services
- Template substitutions
- etc...

There is a lot more you can do, **read the docs:** http://dynaconf.com


## Contribute

Main discussions happens on [t.me/dynaconf](https://t.me/dynaconf) learn more about how to get involved on [CONTRIBUTING.md guide](CONTRIBUTING.md)

# Top Contributors

[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/0)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/0)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/1)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/1)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/2)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/2)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/3)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/3)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/4)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/4)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/5)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/5)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/6)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/6)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/7)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/7)
