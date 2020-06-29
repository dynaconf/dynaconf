# Dynaconf Quick Start

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

## Installation

### Install from [pypi](https://pypi.org/project/dynaconf)

```bash
pip install dynaconf
```

### Initialize Dynaconf on your project

???+ "Using Python Only"

    #### Using Python only

    In your project's root directory run `dynaconf init` command.

    ```bash hl_lines="2"
    cd path/to/your/project/
    dynaconf init -f toml
    ```
    The command output must be:

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

    > ℹ️ You can choose `toml|yaml|json|ini|py` on `dynaconf init -f <fileformat>`,  **toml** is the default and also the most **recommended** format for configuration.

    Dynaconf `init` command creates the following files

    ```plain
    .
    ├── config.py       # Where you import your settings object (required)
    ├── .secrets.toml   # Sensitive data like passwords and tokens (optional)
    └── settings.toml   # Application setttings (optional)
    ```

    === "your_program.py"
        On your own code you import and use **settings** object imported from your **config.py** file
        ```python
        from config import settings

        assert settings.key == "value"
        assert settings.number == 789
        assert settings.a_dict.nested.other_level == "nested value"
        assert settings['a_boolean'] is False
        assert settings.get("DONTEXIST", default=1) == 1
        ```

    === "config.py"
        On this file a new instance of **Dynaconf** settings object is
        initialized and configured.

        ```python
        from dynaconf import Dynaconf

        settings = Dynaconf(
            settings_files=['settings.yaml', '.secrets.yaml'],
        )
        ```
        More options described on [Dynaconf Configuration](/configuration/)

    === "settings.toml"
        **Optionally** store settings in a file (or in multiple files)
        ```toml
        key = "value"
        a_boolean = false
        number = 1234
        a_float = 56.8
        a_list = [1, 2, 3, 4]
        a_dict = {hello="world"}

        [a_dict.nested]
        other_level = "nested value"
        ```
        More details in [Settings Files](/settings_files/)

    === ".secrets.toml"
        **Optionally** store sensitive data in a local only file `.secrets.toml`
        ```toml
        password = "s3cr3t"
        token = "dfgrfg5d4g56ds4gsdf5g74984we5345-"
        message = "This file doesn't go to your pub repo"
        ``` 

        > ⚠️ `dynaconf init` command puts the `.secrets.*` in yout `.gitignore` to avoid it to be exposed on public repos but it is your responsibility to keep it safe in your local environment, also the recommendation for production environments is to use the built-in support for Hashicorp Vault service for password and tokens.
 
        ```ini
        # Secrets doesn't go to public repos
        .secrets.*
        ```

        read more on [Secrets](/secrets/)

    === "env vars"
        **Optionally** override using prefixed environment variables. (`.env` files are also supported)

        ```bash
        export DYNACONF_NUMBER=789
        export DYNACONF_FOO=false
        export DYNACONF_DATA__CAN__BE__NESTED=value
        export DYNACONF_FORMATTED_KEY="@format {this.FOO}/BAR"
        export DYNACONF_TEMPLATED_KEY="@jinja {{ env['HOME'] | abspath }}"
        ```

    ---

    > ℹ️ You can create the files yourself instead of using the `dynaconf init` command and it give any name you want instead of the default `config.py` (the file must be in your importable python path)

??? "Or using Flask"

    #### Using Flask

    === "app.py"
        In your Flask project import `FlaskDynaconf` extension and initialize as a Flask extension.
        ```python hl_lines="2 6"
        from flask import Flask
        from dynaconf import FlaskDynaconf

        app = Flask(__name__)

        FlaskDynaconf(app, settings_files=["settings.toml"])
        ```

        Across your Flask application you can access all the settings variables direct from `app.config` that is now replaced by a dynaconf settings instance.

        ```python
        @app.route("/a_view)
        def a_view():
            app.config.NAME == "BRUNO"
            app.config['DEBUG'] is True
            app.config.SQLALCHEMY_DB_URI == "sqlite://data.db"
        ```

    === "settings.toml"
        **Optionally** store settings in a file using layered environments.

        ```toml
        [default]
        key = "value"
        a_boolean = false
        number = 1234
        
        [development]
        key = "development value"
        SQLALCHEMY_DB_URI = "sqlite://data.db"

        [production]
        key = "production value"
        SQLALCHEMY_DB_URI = "postgresql://..."
        ```

        > ℹ️ On Flask settings files are layered in multiple environments by default, you can disable it passing `environments=False` to FlaskDynaconf extension.

        More details in [Settings Files](/settings_files/)

    === ".secrets.toml"
        **Optionally** store sensitive data in a local only file `.secrets.toml`
        ```toml
        [development]
        password = "s3cr3t"
        token = "dfgrfg5d4g56ds4gsdf5g74984we5345-"
        message = "This file doesn't go to your pub repo"
        ``` 

        > ⚠️ put `.secrets.*` in yout `.gitignore` to avoid it to be exposed on public repos but it is your responsibility to keep it safe in your local environment, also the recommendation for production environments is to use the built-in support for Hashicorp Vault service for password and tokens.
 
        ```ini
        # Secrets doesn't go to public repos
        .secrets.*
        ```

        read more on [Secrets](/secrets/)

    === "env vars"
        **Optionally** override any setting using `FLASK_` prefixed environment variables. (`.env` files are also supported)

        ```bash
        export FLASK_ENV=production
        export FLASK_NUMBER=789
        export FLASK_FOO=false
        ```

    ---

    Dynaconf can also **load your Flask extensions** for you see more details in [Flask Extension](/flask/)


??? "Or using Django"

    #### Using Django

    Ensure you have `DJANGO_SETTINGS_MODULE` exported:

    ```bash
    export DJANGO_SETTINGS_MODULE=yourproject.settings
    ```

    On the same folder where your `manage.py` is located run `dynaconf init` command.

    ```bash hl_lines="1"
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

    > ℹ️ On Django the recommended file format is **yaml** because it can hold
    complex data structures easier, however you can choose to use toml,json,ini or even keep your settings in .py format.

    === "appname/views.py"
        On your Django views, models and all other places you can now use
        **django.conf.settings** normally because it is replaced by a Dynaconf settings object.

        ```python hl_lines="1 5 6 7 8"
        from django.conf import settings


        def index(request):
            assert settings.DEBUG is True
            assert settings.NAME == "Bruno"
            assert settings.DATABASES.default.name == "db"
            assert settings.get("NONEXISTENT", 2) == 2
        ```

    === "settings.yaml"
        **Optionally** store settings in a file using layered environments.
        this file must be located in the folder where your `manage.py` is located.

        ```yaml
        default:
            ALLOWED_HOSTS:
                - '*'
            INSTALLED_APPS:
                - django.contrib.admin
                - django.contrib.auth
                - django.contrib.contenttypes
                - django.contrib.sessions
                - django.contrib.messages
                - django.contrib.staticfiles 
        production:
            ALLOWED_HOSTS:
                - 'server.prod.com'
        ```

        > ℹ️ On Django settings files are layered in multiple environments by default, you can disable it passing `environments=False` to FlaskDynaconf extension.

        More details in [Settings Files](/settings_files/)

    === ".secrets.yaml"
        **Optionally** store sensitive data in a local only file `.secrets.toml`
        ```yaml
        development:
            SECRET_KEY: 43grng9398534nfkjer
        production:
            SECRET_KEY: vfkjndkjg098gdf90gudfsg
        ``` 

        > ⚠️ put `.secrets.*` in yout `.gitignore` to avoid it to be exposed on public repos but it is your responsibility to keep it safe in your local environment, also the recommendation for production environments is to use the built-in support for Hashicorp Vault service for password and tokens.
 
        ```ini
        # Secrets doesn't go to public repos
        .secrets.*
        ```

        read more on [Secrets](/secrets/)

    === "env vars"
        **Optionally** override any setting using `DJANGO_` prefixed environment variables. (`.env` files are also supported)

        ```bash
        export DJANGO_ENV=production
        export DJANGO_NUMBER=789
        export DJANGO_FOO=false
        export DJANGO_ALLOWED_HOSTS="['*']"
        export DJANGO_DEBUG=false
        export DJANGO_DATABASES__default__NAME=othername
        ```

    === "projectname/settings.py"
        Once initialized dynaconf includes the following on the bottom of your
        existing `settings.py` and you need to keep these lines there.

        ```py
        # HERE STARTS DYNACONF EXTENSION LOAD
        import dynaconf  # noqa
        settings = dynaconf.DjangoDynaconf(__name__)  # noqa
        # HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)
        ```

    ---

    More details in [Django Extension](django/)

---

!!! tip
    The `dynaconf` CLI has more useful commands such as `list | export`, `init`, `write` and `validade` read more on [CLI](/cli/)

## Defining your settings variables

Dynaconf prioritizes the use of [environment variables](/envvars/) and 
you can optionally store settings in [Settings Files](/settings_files/) using any of `toml|yaml|json|ini|py` extension.

### On env vars

[environment variables](/envvars/) are loaded by Dynaconf if prefixed either with
`DYNACONF_` or a `CUSTOM_` name that you can customize on your settings instance, or
`FLASK_` and `DJANGO_` respectivelly if you are using extensions.

```bash
export DYNACONF_FOO=BAR                      # string value
                                             # default DYNACONF_ prefix

export DYNACONF_NUMBER=123                   # automatically loaded as int

export DJANGO_ALLOWED_HOSTS="['*', 'other']" # DJANGO_ extension prefix
                                             # automatically loaded as a list

export FLASK_DEBUG=true                      # FLASK_ extension prefix  
                                             # automatically loaded as boolean

export CUSTOM_NAME=Bruno                     # CUSTOM_ prefix as specified in
                                             # Dynaconf(envvvar_prefix="custom")

export DYNACONF_NESTED__LEVEL__KEY=1         # Double underlines
                                             # denotes nested settings
                                             # nested = {
                                             #     "level": {"key": 1}
                                             # }
```

More details on [environment variables](/envvars/).

### On files

**Optionally** you can store settings in files, dynaconf supports multiple
file formats, you are recommended to choose one format but you can also use
mixed settings formats across your application.

#### Supported formats

- **.toml** - Default and **recommended** file format.
- **.yaml|.yml** - Recommended for Django applications.
- **.json** - Usefull to reuse existing or exported settings.
- **.ini** - Useful to reuse legacy settings.
- **.py** - **Not Recommended** but supported for backwards compatibility.
- **.env** - Useful to automate the loading of environment variables.

!!! info
    Create your settings in desired format and specify it on `settings_files`
    argument on your dynaconf instance or pass it in `-f <format>` if using `dynaconf init` command.

!!! tip
    Can't find the file format you need for your settings?
    You can create your custom loader and read any data source.
    read more on [extending dynaconf](/advanced/)

#### Reading settings from files

On files by default dynaconf loads all the existing keys and sections
as first level settings.

=== "settings.toml"
    ```toml
    name = "Bruno"
    ```

=== "settings.yaml"
    ```yaml
    name: Bruno
    ```

=== "settings.json"
    ```json
    {"name": "Bruno"}
    ```

=== "settings.ini"
    ```ini
    name = 'Bruno'
    ```

=== "settings.py"
    ```py
    NAME = "Bruno"
    ```
    > ⚠️ on `.py` files dynaconf only read UPPERCASE variables.

Then on your application code:

```python
settings.name == "Bruno"
```

#### Layered environments on files

It is also possible to make dynaconf to read the files separated by layered 
environments so each section or first level key is loaded as a
distinct environment.

=== "config.py"
    ```py
    settings = Dynaconf(environments=True)
    ```

=== "settings.toml"
    ```toml
    [default]
    name = ""
    [development]
    name = "developer"
    [production]
    name = "admin"
    ```

=== "settings.yaml"
    ```yaml
    default:
        name: ''
    development:
        name: developer
    production:
        name: admin
    ```

=== "settings.json"
    ```json
    {
        "default": {
            "name": ""
        },
        "development": {
            "name": "developer"
        },
        "production": {
            "name": "admin"
        }
    }
    ```

=== "settings.ini"
    ```ini
    [default]
    name = ""
    [development]
    name = "developer"
    [production]
    name = "admin"
    ```


> ℹ️ You can define custom environment using the name you want
`[default]` and `[global]` are the only environments that are special.
You can for example name it `[testing]` or `[anything]`

=== "program.py"

    Then in your program you can use environment variables 
    to switch environments.

    `#!bash export ENV_FOR_DYNACONF=development`

    ```python
    settings.name == "developer"
    ```

    `#!bash export ENV_FOR_DYNACONF=production`

    ```python
    settings.name == "admin"
    ```

!!! warning
    On **Flask** and **Django** extensions the default behaviour is already
    the layered environments.
    Also to switch the environment you use `#!bash export FLASK_ENV=production` or `#!bash export DJANGO_ENV=production` respectivelly. 

!!! tip
    It is also possible to switch environments programatically passing
    `env="development"` to `Dynaconf` class on instantiation.


Read more on [Settings Files](/settings_files/)

## Reading settings variables

An instance of `Dynaconf settings` is a **dict** like object that provides
multiple ways to access variables.

```py
from path.to.project.config import settings
# or
from django.conf import settings
# or
settings = app.config  # flask

# reading settings variables

settings.username == "admin"                  # dot notation
settings.PORT == settings.port == 9900        # case insensitive
isinstance(settings.port, int)                # automatic type casting
settings.databases.name == "mydb"             # Nested keys traversing
settings['password'] == "secret123"           # dict like item access
settings['databases.schema'] == "main"        # Nested items traversing
settings.get("nonexisting", "default value")  # Default values just like a dict
settings("number", cast=int)                  # customizable forcing of casting

for key, value in settings:                   # dict like iteration
    print(key, value)
```

## Validating your settings

Dynaconf offers the `Validator` object for you to define rules for
your settings **schema**, this works in a declarative way and you can
validate your settings in 2 ways.

??? "Writing Validators as Python objects"

    On your **config.py**
    ```py
    from dynaconf import Dynaconf, Validator

    settings = Dynaconf(
        validators=[
            Validator("name", eq="Bruno") & Validator("username", ne="admin"),
            Validator("port", gte=5000, lte=8000),
            Validator("host", must_exist=True) | Validator("bind", must_exist=True)
        ]
    )
    ```

    Once passed in on `validators` argument, Dynaconf will evaluate each of
    the rules before your settings are first read.

    Alternative way is registering validators using.

    ```py
    settings.validators.register(Validator("field", **rules))
    ```

    You can also force the earlier validation placing a call to `validate` 
    after your settings instantiation.

    ```py
    settings.validators.validate()
    ```

    In case of errors it will raise `ValidationError` and exit with status 1 (useful for CI)

??? "Writing Validators as a toml file"

    You can also alternativelly place a `dynaconf_validators.toml` file in the
    root of your project.

    ```toml
    [development]
    name = {must_exist=true}
    port = {gte=5000, lte=9000}
    ```

    Following the same rules used in the `Validator` class, then you can trigger the validation via command line using.

    ```bash
    dynaconf -i config.settings validate
    ```

Read more on [Validation](/validation/)

## Dependencies

### Vendored

Dynaconf core has no dependency it is using vendored copies of external
libraries such as **python-box, click, python-dotenv, ruamel-yaml, python-toml**

### Optional dependencies

To use external services such as **Redis** and **Hashicorp Vault** it is necessary
to install additional dependencies using pip `[extra]` argument.

**Vault**

```bash
pip install dynaconf[vault]
```

**Redis**

```bash
pip install dynaconf[redis]
```

Read more on [external loaders](/loaders/)

## License

This project is licensed under the terms of the MIT license.
