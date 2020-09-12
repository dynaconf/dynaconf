# Settings Files

**Optionally** you can store settings in files, dynaconf supports multiple
file formats, you are recommended to choose one format but you can also use
mixed settings formats across your application.

!!! tip
    You are not required to use settings files, if not specified dynaconf
    can load your data only from [environment variables](/envvars/)

## Supported formats

- **.toml** - Default and **recommended** file format.
- **.yaml|.yml** - Recommended for Django applications.
- **.json** - Useful to reuse existing or exported settings.
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

## Reading settings from files

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

!!! info
    The default encoding when loading the settings files is `utf-8` and it can be customized
    via `encoding` parameter.

## Settings file location

Dynaconf will search files specified in `settings_file` option starting the search tree
on the current working dir (the directory where you program is located).

Ex:

```py
from dynaconf import Dynaconf

settings = Dynaconf(settings_files=["settings.toml", "/etc/program/foo.yaml"])
```

### settings.toml

In the above example, dynaconf will try to load `settings.toml` from the same
directory where the program is located, also known as `.` and then will
keep traversing the folders in backwards order until the root is located.

root is either the path where the program was invoked, or the O.S root or the root
specified in `root_path`.

### /etc/program/foo.yaml

Dynaconf will then recognize this as an absolute path and will try to load it directly from
the specified location.


---

## Local Settings files

For each file specified in `settings_files` dynaconf will also try to load
an optional `name`**.local.**`extension`.

For example, `settings_files=["settings.toml"]` will make dynaconf to search for `settings.toml` and then also search for `settings.local.toml`


---

## Includes

You can also specify includes so dynaconf can include those settings after the normal loading.

### as a parameter

```py
settings = Dynaconf(includes=["path/to/file.toml", "or/a/glob/*.yaml])
```

### as a variable in a file

```toml
dynaconf_include = ["path/to/file.toml"]
key = value
anotherkey = value
```

---

## Layered environments on files

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
    Also to switch the environment you use `#!bash export FLASK_ENV=production` or `#!bash export DJANGO_ENV=production` respectively. 

!!! tip
    It is also possible to switch environments programmatically passing
    `env="development"` to `Dynaconf` class on instantiation.
