When create your instance of `Dynaconf` **settings** object
there are some customizable parameters.


## On instance options
Configurations can be passed explicitly to your instance.

```py
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="MYPROGRAM",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True,
    env_switcher="MYPROGRAM_ENV",
    **more_options
)
```

## on environment options

And can also be exported as environment variables following the rule of being all `UPPERCASE` and suffixed with `_FOR_DYNACONF`.

```bash
export ENVVAR_PREFIX_FOR_DYNACONF=MYPROGRAM
export SETTINGS_FILES_FOR_DYNACONF="['settings.toml',  ...]"
export ENVIRONMENTS_FOR_DYNACONF=true
export LOAD_DOTENV_FOR_DYNACONF=true
export ENV_SWITCHER_FOR_DYNACONF=MYPROGRAM_ENV
```

## Available options

!!! info
    When exporting as env vars ensure to use UPPERCASE and add the `_FOR_DYNACONF` suffix. example: `export AUTO_CAST_FOR_DYNACONF=true`

!!! tip
    Env vars are casted using TOML parser, so `=FOO` is `str`, `=42` is `int`, `=42.1` is `float`, `=[1, 2]` is a `list` and `={foo="bar"}` is a `dict` and finally `=true` is a boolean. (to force a string value enclose it on quotes: `="'42'"` is `str, '42'`)

### **auto_cast**
Auto cast is the ability of using tokens to specify the type casting for settings variables.
ex: `@format {env[HOME]}`, `@int 32`, `@json {...}`, this options disables that feature.

- type: bool
- default: true

---

### **commentjson_enabled**

Enables comments in JSON settings files, to work `commentjson` must be installed `pip install commentjson`

- type: bool
- default: false

---

### **core_loaders**

The list of enabled loaders that dynaconf will use to load settings files, if your application is using only `YAML` you can for example change it to `['YAML']` so dynaconf stops trying to load `toml` and other formats.

- type: list
- default: `[‘YAML’, ‘TOML’, ‘INI’, ‘JSON’, ‘PY’]`

---

### **default_env**

When `environments` is set, dynaconf will use this value as the environment holding the default values,
ex: in a `toml` file it will be `[default]` section.

- type: str
- default: "default"

---

### **dotenv_override**

When `load_dotenv` is enabled, this controls if variables in `.env` will override the values exported as env vars.

- type: boolean
- default: false

---

### **dotenv_path**

Sets the path for the `.env` file and it can be full path or just the directory.

- type: str
- default: "." (or the same as project_root)

---

### **dotenv_verbose**

Controls the verbosity of dotenv loader.

- type: boolean
- default: false

---

### **encoding**

Which encoding to use when loading settings files.

- type: str
- default: "utf-8"

---

### **environments**

Controls if Dynaconf will work in a multi layered environment system allowing `[default]`, `[development]`, `[production]` and other separation of environments.

- type: boolean or a list
- default: false

---

### **envvar**

The variable to change the location of settings module using environment variables.
ex: `export SETTINGS_FILE_FOR_DYNACONF=another/path/settings.toml`

- type: str
- default: "SETTINGS_FILE_FOR_DYNACONF"

---

### **envvar_prefix**

The prefix for dynaconf to load values from environment variables, in your program you might want users
to export using your app name ex: `export MYPROGRAM_DEBUG=true`

- type: str
- default: "DYNACONF"

---

### **env**
When `environments` is set, this controls the current environment for the runtime execution.
usually this is set using environment variable.

```bash
export ENV_FOR_DYNACONF=production
```

Or per execution: `ENV_FOR_DYNACONF=production program.py`

- type: str
- default: "development"

---

### **env_switcher**

By default `ENV_FOR_DYNACONF` is the variable to switch envs, but you can set this to another variable name.
ex: `MYPROGRAM_ENV=production`

- type: str
- default: "ENV_FOR_DYNACONF"

---

### **force_env**

When `environments` is enabled it might be useful to force an specific env for testing purposes.

- type: str
- default: None

---

### **fresh_vars**

In some cases you might need some variables to be always reloaded from source without the need to 
reload the application. Variables passed in this list when accessed will always trigger a reload from
source, settings files will be read, envvars parsed and external loaders connected.

- type: list
- default: []

ex: `fresh_vars=["password"]` so when accessing `settings.password` it will be read from source not cache.

---

### **includes**

After the load of files specified in `settings_files` Dynaconf will load all the files added to `includes` in a post load process.

- type: list
- default: []

!!! tip
    Includes can also be added inside files itself, ex:
    ```toml
    includes: ['otherfile.toml']
    key: "value"
    ```
    Or using env vars:
    ```bash
    export INCLUDES_FOR_DYNACONF="['otherfile.toml', 'path/*.yaml']"
    ```
    **Includes allows the use of globs**

---

### **loaders**

The list of loaders Dynaconf will trigger after its core loaders, this list is useful to include
[custom loaders](/advanced/#custom loaders) and also to control the loading of env vars as the last step.

!!! warning
    By default the `env_loader` will be latest on this list, so it ensures environment variables has
    the priority following the Unix philosophy.

- type: list
- default: ['dynaconf.loaders.env_loader']

Learn more about [loaders](/advanced/)

---

### **load_dotenv**

When turned on dynaconf will try to load the variables from a `.env` file.

- type: bool
- default: false

---

### **lowercase_read**

By default dynaconf allows the access of first level vars as lowercase, so `settings.foo` and `settings.FOO` are equivalent (case insensitive). IF needed it can be disabled.

- type: bool
- default: true

---

### **merge_enabled**

If the specified Dynaconf enters in a **GLOBAL MERGE** mode and when loading new files or sources will not override but merge data structures by default.

- type: bool
- default: false

ex:

```toml
# settings.toml
[server]
data = {port=8888}
```

```toml
# other.toml
[server]
data = {address='server.com'}
```

With `merge_enabled` the ending `settings.server` will be 

```python
{"port": 8888, "address": "server.com"}
```
otherwise it will be only what is specified in the latest loaded file. read more about [merging strategies](/merging)

---

### **nested_separator**

One of the [merging strategies](/merging) is the use of `__` to access nested level data structures. By default the separator is `__` (double underline), this variable allows you to change that.

!!! warning
    Choose something that is suitable for env vars, usually you don't need to change this variable.

- type: str
- default: "__"

ex:
```bash
export DYNACONF_DATABASES__default__ENGINE__Address="0.0.0.0"
```

generates:

```python
DATABASES = {
    "default": {
        "ENGINE": {
            "Address": "0.0.0.0"
        }
    }
}
```

!!! Warning
    On windows env vars are all transformed to upper case.

---

### **preload**

Sometimes you might need to load some file before Dynaconf starts looking for  its `settings_files` or `includes`, you can have for example a `dynaconf.toml` to hold dynaconf's configuration.

- type: list
- default: []

---

### **redis_enabled**

If set to `true` dynaconf will include `dynaconf.loaders.redis_loaders` in the `loaders` list.

- type: bool
- default: false

---

### **redis**

When `redis_enables` is true, a dictionary holding redis settings.

- type: dict
- default:
    ```py
    {
        "host": "REDIS_HOST_FOR_DYNACONF" or "localhost",
        "port": int("REDIS_PORT_FOR_DYNACONF" or 6379),
        "db": int("REDIS_DB_FOR_DYNACONF" or 0),
        "decode_responses": "REDIS_DECODE_FOR_DYNACONF" or True,
    }
    ```
---

### **root_path**

The working path for dynaconf to use as starting point when searching for files:

- type: str
- default: None

Read more on [settings_files](/settings_files/#load)

---

### **secrets**

This variable is useful for CI and Jenkins, usually set as environment variable pointing to a file
containing the secrets to be loaded.

- type: str
- default: None

ex: `export SECRETS_FOR_DYNACONF=path/to/secrets.yaml`

---

### **settings_file** or **settings_files**

!!! info
    This variable is required.

The path for the files you wish dynaconf to load the settings from.
It can be `settings_file` (singular) or `settings_files` (multiple).

- type: str or list
- default: []

Starting on v3.0.0 dynaconf will load only files specified on this variables.

Must be a `list`:

```py
settings_files=["file1.toml", "file2.toml"]
```

or a `str` separated by semicolons or commas.

```py
settings_files="file1.toml;file2.toml"
settings_files="file1.toml,file2.toml"
```

Also it can be a single file.

```py
settings_file="settings.toml"
```

Or specified as env var.

```bash
# singular
export SETTINGS_FILE_FOR_DYNACONF="/etc/program/settings.toml"

# multiple
export SETTINGS_FILES_FOR_DYNACONF="/etc/program/settings.toml;/tmp/foo.yaml"
```

Read more on [settings_files](/settings_files/)

---

### **skip_files**

When using a glob on `includes` you might want dynaconf to ignore some files that matches.

- type: list
- default: None

```py
skip_filess=["path/to/ignored.toml"]

```

---

### **validators**

A list of validators to be triggered right after the `Dynaconf` initialization.

- type: list
- default: []

```py
validators=[
    Validator("FOO", must_exist=True)
]
```

---

### **vault_enabled**

If set to `true` dynaconf will include `dynaconf.loaders.vault_loader` in the `loaders` list.

- type: bool
- default: false

---

### **vault**

When `vault_enabled` is true, a dictionary holding vault settings.

- type: dict
- default:

    ```py
    {
        "url": "VAULT_URL_FOR_DYNACONF" or f"{vault_scheme}://{vault_host}:{vault_port}",
        "token": "VAULT_TOKEN_FOR_DYNACONF" or None,
        "cert": "VAULT_CERT_FOR_DYNACONF" or  None,
        "verify": "VAULT_VERIFY_FOR_DYNACONF" or None,
        "timeout": "VAULT_TIMEOUT_FOR_DYNACONF" or None,
        "proxies": "VAULT_PROXIES_FOR_DYNACONF" or None,
        "allow_redirects": "VAULT_ALLOW_REDIRECTS_FOR_DYNACONF" or None,
    }
    ```
Read more on [Secrets](/secrets/)

---

### **yaml_loader**

The loader to use for YAML.

- type: str
- default: full_load

Options: safe_load, unsafe_load, full_load

---


