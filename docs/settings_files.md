# Settings Files

**Optionally** you can store settings in files, dynaconf supports multiple
file formats, you are recommended to choose one format but you can also use
mixed settings formats across your application.


!!! tip
    You are not required to use settings files, if not specified dynaconf
    can load your data only from [environment variables](envvars.md)

## Supported formats

- **.toml** - Default and **recommended** file format.
- **.yaml|.yml** - Recommended for Django applications (see [YAML Caveats](#yaml-caveats)).
- **.json** - Useful to reuse existing or exported settings.
- **.ini** - Useful to reuse legacy settings.
- **.py** - **Not Recommended** but supported for backwards compatibility.
- **.env** - Useful to automate the loading of environment variables.

!!! info
    Create your settings in the desired format and specify it on `settings_files`
    argument on your dynaconf instance or pass it in `-f <format>` if using `dynaconf init` command.

!!! tip
    Can't find the file format you need for your settings?
    You can create your custom loader and read any data source.
    read more on [extending dynaconf](advanced.md)

!!! warning
    To use the `.ini` or `.properties` file format you need to install an extra dependency
    `pip install configobj` or `pip install dynaconf[ini]`

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

## Loading setting files

Dynaconf will start looking for each file defined in `settings_files` from the folder where your entry point python file is located (like `app.py`). Then, it will look at each parent down to the root of the system. For each visited folder, it will also try looking inside a `/config` folder.

- If you define [root_path](configuration.md/#root_path), it will look start looking from there, instead. Keep in mind that `root_path` is relative to `cwd`, which is from where the python interpreter was called.
- Absolute paths are recognized and dynaconf will attempt to load them directly.
- For each file specified in `settings_files` dynaconf will also try to load an optional `name`**.local.**`extension`. Eg, `settings_file="settings.toml"` will look for `settings.local.toml` too.
- Globs are accepted.

Define it in your settings instance or export the corresponding envvars.

```python
# default
settings = Dynaconf(settings_files=["settings.toml", "*.yaml"])

# using root_path
settings = Dynaconf(
    root_path="my/project/root",
    settings_files=["settings.toml", "*.yaml"]
)
```

```bash
export ROOT_PATH_FOR_DYNACONF='my/project/root'
export SETTINGS_FILES_FOR_DYNACONF='["settings.toml", "*.yaml"]'
```

!!! info
    To use `python -m module`, where the module uses dynaconf you will need to
    specify your `settings.toml` path, for example, like this: `settings_file="module/config/settings.toml"`.

---

## Includes and Preloads

If you need, you can specify files to be loaded before or after the `settings_files` using the options [preload](configuration.md#preload) and [includes](configuration.md#includes). Their loading strategy is more strict, and will use `root_path` as the basepath for the relative paths provided. If `root_path` is not defined, `includes` will also try using the last found settings directory as the basepath.

They can be defined in the Dynaconf instance or in a file:

```py
# in Dynaconf instance
settings = Dynaconf(
    includes=["path/to/file.toml", "or/a/glob/*.yaml"],
    preload=["path/to/file.toml", "or/a/glob/*.yaml"])
```

or

```toml
# in toml file
dynaconf_include = ["path/to/file.toml"]
key = value
anotherkey = value
```

---

## Layered environments on files

It is also possible to make dynaconf read the files separated by layered
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

!!! info
    You can define a custom environment using the name you want, like `[testing]` or `[anything]`

    `[default]` and `[global]` are the only environments that are special.

=== "program.py"

    Then in your program, you can use environment variables
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

### YAML Caveats

#### Nonetypes

Yaml parser used by dynaconf (ruamel.yaml) reads undefined values as `None` so

```yaml
key:
key: ~
key: null
```

All those 3 keys will be parsed as python's `None` object.

When using a validator to set a default value for those values you might want to use one of:

```py
Validator("key", default="thing", apply_default_on_none=True)
```

This way dynaconf will consider the default value even if the setting is `None` on yaml.

or on yaml you can set the value to `@empty`

```yaml
key: "@empty"
```
>> **NEW** in 3.1.9
