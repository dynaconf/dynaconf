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
    Env vars are cast using the TOML parser, so `=FOO` is `str`, `=42` is `int`, `=42.1` is `float`, `=[1, 2]` is a `list` and `={foo="bar"}` is a `dict` and finally `=true` is a boolean. (to force a string value enclose it in quotes: `="'42'"` is `str, '42'`)

### **apply_default_on_none**

> type=`bool`, default=`False` </br>
> env-var=`DOTTED_LOOKUP_FOR_DYNACONF`

YAML reads empty values as `None` in this case if you want to have `Validator` defaults applied
to the `None` values you must set `apply_default_on_none` to `True` on `Dynaconf` class or specific on `Validator` instance.

### **auto_cast**

> type=`bool`, default=`True` </br>
> env-var=`AUTO_CAST_FOR_DYNACONF`

Auto cast is the ability of using special tokens to cast settings variables.
ex: `@format {env[HOME]}`, `@int 32`, `@json {...}`

---

### **commentjson_enabled**

> type=`bool`, default=`False` </br>
> env-var=`COMMENTJSON_ENABLED_FOR_DYNACONF`

Enables comments in JSON settings files, but `commentjson` must be installed, i.e.: `pip install commentjson`

---

### **core_loaders**

> type=`list`, default=`[‘YAML’, ‘TOML’, ‘INI’, ‘JSON’, ‘PY’]` </br>
> env-var=`CORE_LOADERS_FOR_DYNACONF`

The list of enabled loaders that dynaconf will use to load settings files, if your application is using only `YAML` you can for example change it to `['YAML']` so dynaconf stops trying to load `toml` and other formats.

---

### **default_env**

> type=`str`, default=`"default"` </br>
> env-var=`DEFAULT_ENV_FOR_DYNACONF`

When `environments=True`, this defines the environment name that will hold the default/fallback values.

Eg.

```toml
# settings.toml

[my_default]
test_value = "test value from default"
other_value = "other value from default"

[development]
# no test_value here
other_value = "other value from dev"
```

```py
>>> settings = Dynaconf(
...     settings_file="settings.toml",
...     environments=True,
...     default_env="my_default",
...     env="development", # this is the active env, by default
... )

>>> settings.other_value
"other value from dev"

>>> settings.test_value
"test value from default" # fallback to `my_default`
```

!!! note
		The `default_env` is not the environment that will be active on startup. For this, see [`env`](configuration.md#env).


---

### **dotenv_override**

> type=`bool`, default=`False` </br>
> env-var=`DOTENV_OVERRIDE_FOR_DYNACONF`

When `load_dotenv` is enabled, this controls if variables in `.env` will override the values exported as env vars.

---

### **dotenv_path**

> type=`str`, default=`"."` (or the same as _project_root_) </br>
> env-var=`DOTENV_PATH_FOR_DYNACONF`

Sets the location of the `.env` file to either the full path or the containing directory.

---

### **dotenv_verbose**

> type=`bool`, default=`False` </br>
> env-var=`DOTENV_VERBOSE_FOR_DYNACONF`

Controls the verbosity of dotenv loader.

---

### **dotted_lookup**

> type=`bool`, default=`True` </br>
> env-var=`DOTTED_LOOKUP_FOR_DYNACONF`

By default dynaconf reads `.` as separator when setting and reading values.
this feature can be disabled by setting `dotted_lookup=False`

!!! tip
    This can also be set per file using `dynaconf_dotted_lookup: false` in the top level of the file and works for setting values. For reading you can pass `setting.get("key.other", dotted_lookup=False)`

---

### **encoding**

> type=`str`, default=`"utf-8"` </br>
> env-var=`ENCODING_FOR_DYNACONF`

Which encoding to use when loading settings files.

---

### **environments**

> type=`bool`, default=`False` </br>
> env-var=`ENVIRONMENTS_FOR_DYNACONF`

Controls if dynaconf will work in a multi-layered environment system allowing `[default]`, `[development]`, `[production]` and other environment separations.

---

### **envvar**

> type=`str`, default=`SETTINGS_FILE_FOR_DYNACONF` </br>
> env-var=`ENVVAR_FOR_DYNACONF`

Sets an environment variable name that will be used to load the settings files.

Eg:

```bash
# sets MY_SETTINGS_PATH as the new env var that defines the paths to the settings files.
export ENVVAR_FOR_DYNACONF="MY_SETTINGS_PATH"

# now its value will override *settings_file* or SETTINGS_FILE_FOR_DYNACONF values
export MY_SETTINGS_PATH="path.to.settings"
```

!!! warning "Legacy Option"
    The preferred way of defining setting files is through [setting_file](https://www.dynaconf.com/configuration/#settings_file-or-settings_files). Consider if you really need to use this.

---

### **envvar_prefix**

> type=`str`, default=`"DYNACONF"` </br>
> env-var=`ENVVAR_PREFIX_FOR_DYNACONF`

The prefix used by dynaconf to load values from environment variables. You might want your users
to export values using your app name, ex: `export MYPROGRAM_DEBUG=true`

**new in 3.2.7**

- The prefix  can be a comma separated list of prefixes, ex: `export MYPROGRAM_DEBUG=true` and `export MYAPP_DEBUG=true` will be loaded as `settings.DEBUG` if `ENVVAR_PREFIX_FOR_DYNACONF=MYPROGRAM,MYAPP`

---

### **env**

> type=`str`, default=`"development"` </br>
> env-var=`ENV_FOR_DYNACONF`

When `environments` is set, this controls the current environment used in runtime.
This is usually set using an environment variable.

```bash
export ENV_FOR_DYNACONF=production
```

Or per execution: `ENV_FOR_DYNACONF=production program.py`


**new in 3.2.7**

- The `env` can be a comma separated list of envs, ex: `export ENV_FOR_DYNACONF=production,staging` will activate both `production` and `staging` environments, and variables from both layers will be loaded in the order they are defined.

---

### **env_switcher**

> type=`str`, default=`"ENV_FOR_DYNACONF"` </br>
> env-var=`ENVVAR_SWITCHER_FOR_DYNACONF`

By default `ENV_FOR_DYNACONF` is the variable used to switch envs, but you can set this to another variable name.
ex: `MYPROGRAM_ENV=production`

---

### **filtering_strategy**

> type=`class`, default=`None` </br>
> env-var=`FILTERING_STRATEGY_FOR_DYNACONF`

Callable accepting data to be filtered, built-ins currently include [PrefixFilter](strategies.md#filtering).

---

### **force_env**

> type=`str`, default=`None` </br>
> env-var=`FORCE_ENV_FOR_DYNACONF`

When `environments` is enabled it might be useful to force an specific env for testing purposes.

---

### **fresh_vars**

> type=`list`, default=`[]` </br>
> env-var=`FRESH_VARS_FOR_DYNACONF`

In some cases you might need some variables to be always reloaded from source without the need to
reload the application. Variables passed in this list when accessed will always trigger a reload from
source, settings files will be read, envvars parsed and external loaders connected.

- ex: `fresh_vars=["password"]` so when accessing `settings.password` it will be read from source not cache.

---

### **includes**

> type=`list | str`, default=`[]` </br>
> env-var=`INCLUDES_FOR_DYNACONF`

After loading the files specified in `settings_files` dynaconf will load all the files added to `includes` in a post-load process.
Note that:

- Globs are allowed
- When relative paths are given it will use [root_path](configuration.md#root_path) as their basedir.
- If `root_path` is not defined explicitly, will fallback to the directory of the last loaded setting or
to the `cwd`. Eg:

```python
# will look for src/extra.yaml
Dynaconf(root_path="src/", includes="extra.yaml")

# will look for conf/extra.yaml
Dynaconf(settings_files="conf/settings.yaml", includes="extra.yaml")

# will look for $PWD/extra.yaml
Dynaconf(includes="extra.yaml")
```

!!! tip
    Includes can also be added inside files itself, ex:

    ```toml
    dynaconf_include: ['otherfile.toml'] # or
    dynaconf_include: 'otherfile.toml'
    key: "value"
    ```

    Or using env vars:

    ```bash
    export INCLUDES_FOR_DYNACONF="['otherfile.toml', 'path/*.yaml']"
    ```

---

### **loaders**

> type=`list`, default=`['dynaconf.loaders.env_loader']` </br>
> env-var=`LOADERS_FOR_DYNACONF`

The list of loaders dynaconf will trigger after its core loaders, this list is useful to include
[custom loaders](advanced.md/#custom loaders) and also to control the loading of env vars as the last step.

!!! warning
    By default the `env_loader` will be latest on this list, so it ensures environment variables has the priority following the Unix philosophy.

Learn more about [loaders](advanced.md)

---

### **load_dotenv**

> type=`bool`, default=`False` </br>
> env-var=`LOAD_DOTENV_FOR_DYNACONF`

When turned on, dynaconf will try to load the variables from a `.env` file.

---

### **lowercase_read**

> type=`bool`, default=`True` </br>
> env-var=`LOWERCASE_READ_FOR_DYNACONF`

By default dynaconf allows the access of first level vars as lowercase, so `settings.foo` and `settings.FOO` are equivalent (case insensitive). IF needed it can be disabled.

---

### **merge_enabled**

> type=`bool`, default=`False` </br>
> env-var=`MERGE_ENABLED_FOR_DYNACONF`

If the specified Dynaconf enters in a **GLOBAL MERGE** mode and when loading new files or sources will not override but merge data structures by default.

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

Otherwise it will be only what is specified in the latest loaded file. read more about [merging strategies](merging.md)

---

### **nested_separators**

> type=`str`, default=`"__"` (double underescore) </br>
> env-var=`NESTED_SEPARATOR_FOR_DYNACONF`

One of the [merging strategies](merging.md) is the use of `__` to access nested level data structures. By default the separator is `__` (double underline), this variable allows you to change that.

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

To access list by indexing

> type=`str`, default=`"___"` (triple underescore) </br>
> env-var=`INDEX_SEPARATOR_FOR_DYNACONF`

ex:

```bash
export DYNACONF_DATABASES__default__WORKERS___0__Address="1.1.1.1"
export DYNACONF_DATABASES__default__WORKERS___1__Address="2.2.2.2"
```

generates:

```python
DATABASES = {
    "default": {
        "ENGINE": {
            "Address": "0.0.0.0"
        },
        "WORKERS": [
            {"Address": "1.1.1.1"},
            {"Address": "2.2.2.2"} 
        ]
    }
}
```

!!! warning
    Choose something that is suitable for env vars, usually you don't need to change this variable.

!!! Warning
    On windows env vars are all transformed to upper case.

---

### **preload**

> type=`list | str`, default=`[]` </br>
> env-var=`PRELOAD_FOR_DYNACONF`

Sometimes you might need to load some file before dynaconf starts looking for its `settings_files` or `includes`, you can have for example a `dynaconf.toml` to hold dynaconf's configuration.

---

### **redis_enabled**

> type=`bool`, default=`False` </br>
> env-var=`REDIS_ENABLED_FOR_DYNACONF`

If set to `True` dynaconf will include `dynaconf.loaders.redis_loaders` in the `loaders` list.

---

### **redis**

> type=`dict`, default=`{ too long, see below }` </br>
> env-var=`REDIS_FOR_DYNACONF`

When `redis_enabled` is true, a dictionary holding redis settings.

```py
default = {
    "host": "REDIS_HOST_FOR_DYNACONF" or "localhost",
    "port": int("REDIS_PORT_FOR_DYNACONF" or 6379),
    "db": int("REDIS_DB_FOR_DYNACONF" or 0),
    "decode_responses": "REDIS_DECODE_FOR_DYNACONF" or True,
}

```

---

### **root_path**

> type=`str`, default=`None` </br>
> env-var=`ROOT_PATH_FOR_DYNACONF`

The working path for dynaconf to use as the starting point when searching for files.

Note that:

- For relative path, uses `cwd` as its basepath
- When not explicitly set, the internal value for `root_path` will be set as follow:
    - The place of the last loaded file, if any files were already loaded
    - CWD

Read more on [settings_files](settings_files.md#load).

!!! note
     The `cwd` is from where the python interpreter was called.

---

### **secrets**

> type=`str`, default=`None` </br>
> env-var=`SECRETS_FOR_DYNACONF`

This variable is useful for CI and Jenkins, usually set as environment variable pointing to a file
containing the secrets to be loaded.

ex: `export SECRETS_FOR_DYNACONF=path/to/secrets.yaml`

---

### **settings_file** (or **settings_files**)

> type=`str | list`, default=`[]` </br>
> env-var=`SETTINGS_FILE_FOR_DYNACONF` or `SETTINGS_FILES_FOR_DYNACONF`

!!! info
    This variable is required since v3.0.0 (see [#361](https://github.com/dynaconf/dynaconf/pull/361))

The path for the files you wish dynaconf to load the settings from.
It can be `settings_file` (singular) or `settings_files` (multiple).

</br>

It can be `list` or `str` separated by semicolons/commas:

```py
settings_files=["file1.toml", "file2.toml"] # list
settings_files="file1.toml;file2.toml" # semicolons separator
settings_files="file1.toml,file2.toml" # commas separator
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

Read more on [settings_files](settings_files.md) </br>

---

### **skip_files**

> type=`list`, default=`None` </br>
> env-var=`SKIP_FILES_FOR_DYNACONF`

When using a glob on `includes` you might want dynaconf to ignore some files that matches.

```py
skip_files=["path/to/ignored.toml"]

```

---

### **sysenv_fallback**

> type=`bool | list[str]`, default=`False` </br>
> env-var=`SYSENV_FALLBACK_FOR_DYNACONF`

Defines if dynaconf will try to load system environment variables (unprefixed)
as a fallback when using `settings.get()`.

Valid options are:

- `False` (default): won't try to load system envvar
- `True`: will try to load sys envvar for any name requested in `get()`
- `list[str]`: will try to load sys envvar for the names provided in the list


</br>

This behaviour can also be defined on a per-call basis by providing
the parameter `sysenv_fallback` to `settings.get()`

Eg:

```python
from dynaconf import Dynaconf

# will look for PATH (uppercase) in the system environment variables
settings = Dynaconf(sysenv_fallback=True)
settings.get("path")

# can be set on a per-call basis
settings = Dynaconf()
settings.get("path", sysenv_fallback=True)

# if a list is used, it filters what names are allowed.
settings = Dynaconf(sysenv_fallback=["path"])
settings.get("path")
settings.get("user") # won't try loading unprefixed USER
```

---

### **validate_on_update**

> type=`False | True | "all"`, default=`False` </br>
> env-var=`VALIDATE_ON_UPDATE_FOR_DYNACONF`

Defines if validation will be triggered when a Dynaconf instance
is updated with the methods `update()`, `set()` or `load_file()`.
Also defines which raising strategy will be used (see more on [Validation](validation.md#trigger-on-data-update)).

Valid options are:

- `False` (default): auto-trigger off
- `True`: trigger as `settings.validate()`, which raises on first errors
- `"all"`: trigger as `settings.validate_all()`, which accumulates errors


</br>

This behaviour can also be defined on a per-call basis. Just provide
the parameter `validate` to any of the data-update methods.

Eg:

```python
settings = Dynaconf(validate_on_update="all")
settings.validators.register(Validator("value_a", must_exist=True))

settings.update({"value_b": "foo"}, validate=False) # will bypass validation
settings.update({"value_b": "foo"}, validate=True) # will call .validate()
settings.update({"value_b": "foo"}) # will call .validate_all()
```

### **validators**

> type=`list`, default=`[]` </br>
> env-var=`VALIDATORS_FOR_DYNACONF`

A list of validators to be triggered right after the `Dynaconf` initialization.

```py
validators=[
    Validator("FOO", must_exist=True)
]
```

### **validate_only_current_env**

> type=`bool`, default=`False` </br>

When `envs` is enabled, defines if validation will be performed only on `default` + `current_env` or if all envs will be validated (even if not activated).

Setting this to `True` can be useful if you have validators that apply only to some `env`s, like requiring a setting in `production` but not in `development`. See [this section](validation.md#validating-only-the-current_env) in the Validation page.

### **validate_only**

> type=`str | list[str] | None`, default=`None` </br>

Will only validate settings that start with the given `str` or any of the `str`s in the `list[str]`. Settings that don't start with these won't be validated. If `None`, will validate all settings as usual.

This setting only applies during `Dynaconf` instantiation. Further calls to `Dynaconf.validators.validate` will use the value passed to the `only` kwarg in that call.

In practice, this forwards `validate_only` to the `only` kwarg during the validation step upon `Dynaconf` instantiation for all `Validator`s passed. Note that this setting has interaction with [`validate_exclude`](#validate_exclude).

Read more about it in the [selective validation](validation.md#selective-validation) section.

### **validate_exclude**

> type=`str | list[str] | None`, default=`None` </br>

Will skip validation of _**any** settings_ that start with the given `str` or any of the `str`s in the `list[str]`. If `None`, won't skip any settings validate all settings as usual.

This setting only applies during `Dynaconf` instantiation. Further calls to `Dynaconf.validators.validate` will use the value passed to the `exclude` kwarg in that call.

In practice, this forwards `validate_exclude` to the `exclude` kwarg during the validation step upon `Dynaconf` instantiation for all `Validator`s passed. Note that this setting has interaction with [`validate_only`](#validate_only).

Read more about it in the [selective validation](validation.md#selective-validation) section.

---

### **vault_enabled**

> type=`bool`, default=`False` </br>
> env-var=`VAULT_ENABLED_FOR_DYNACONF`

If set to `True` dynaconf will include `dynaconf.loaders.vault_loader` in the `loaders` list.

---

### **vault**

> type=`dict`, default=`{ too long, see below}` </br>
> env-var=`VAULT_FOR_DYNACONF`

When `vault_enabled` is true, a dictionary holding vault settings.

```py
default = {
    "url": "VAULT_URL_FOR_DYNACONF" or f"{vault_scheme}://{vault_host}:{vault_port}",
    "token": "VAULT_TOKEN_FOR_DYNACONF" or None,
    "cert": "VAULT_CERT_FOR_DYNACONF" or  None,
    "verify": "VAULT_VERIFY_FOR_DYNACONF" or None,
    "timeout": "VAULT_TIMEOUT_FOR_DYNACONF" or None,
    "proxies": "VAULT_PROXIES_FOR_DYNACONF" or None,
    "allow_redirects": "VAULT_ALLOW_REDIRECTS_FOR_DYNACONF" or None,
}
```

Read more on [Secrets](secrets.md)

---

### **yaml_loader**

> type=`str` (options, see below), default=`"full_load"` </br>
> env-var=`YAML_LOADER_FOR_DYNACONF`

The loader to use for YAML.

Options: `"safe_load"`, `"unsafe_load"`, `"full_load"`
