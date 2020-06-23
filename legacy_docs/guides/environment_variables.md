# Environment variables

## overloading parameters via env vars

All configuration parameters, including **custom** environments and [dynaconf configuration](configuration.html), can be overridden through environment variables.

To override the configuration parameter **{param}**, use an environment variable named **DYNACONF_{PARAM}**. For instance, to override the **"HOST"** configuration parameter, you can run your application with:

```bash
DYNACONF_HOST='otherhost.com' python yourapp.py
```

## .env files

If you don't want to declare the variables on every program call you can run `export DYNACONF_{PARAM}` in your shell or put the values in a `.env` file located in the same directory as your settings files (the root directory of your application or the same folder where your program script is located), variables in `.env` does not overrride existing environment variables.

> **IMPORTANT**: Dynaconf will search for a `.env` on the order explained [here](usage.html). So to avoid conflicts with existing `.env` in parent directories it is recommended to have a `.env` inside your project even if it is empty.

## Precedence and type casting

Environment variables take precedence over all other configuration sources: if the variable is set, it will be used as the value for the parameter even if parameter exists in `settings` files or in `.env`.

Variable values are parsed as if they were **TOML** syntax. As illustration, consider the following examples:

```ini
# Numbers
DYNACONF_INTEGER=42
DYNACONF_FLOAT=3.14

# Text
DYNACONF_STRING=Hello
DYNACONF_STRING="Hello"

# Booleans
DYNACONF_BOOL=true
DYNACONF_BOOL=false

# Use extra quotes to force a string from other type
DYNACONF_STRING="'42'"
DYNACONF_STRING="'true'"

# Arrays must be homogenous in toml syntax
DYNACONF_ARRAY="[1, 2, 3]"
DYNACONF_ARRAY="[1.1, 2.2, 3.3]"
DYNACONF_ARRAY="['a', 'b', 'c']"

# Dictionaries
DYNACONF_DICT="{key='abc',val=123}"
```

> **NOTE:** When exporting compose data types like arrays and dictionaries you must use quotes around the value e.g: `export VARIABLE="['a', 'b', 'c']"` instead of `export VARIABLE=['a', 'b', 'c']`

```python
# toml syntax does not allow `None/null` values so use @none
DYNACONF_NONE='@none None'

# toml syntax does not allow mixed type arrays so use @json
DYNACONF_ARRAY='@json [42, 3.14, "hello", true, ["otherarray"], {"foo": "bar"}]'

# Lazily formatted string can access env vars and settings variables.

# using str.format
DYNACONF_DATABASE_PATH="@format {env[HOME]}/.config/databases/{this.DB_NAME}"

# using jinja2
DYNACONF_DATABASE_PATH="@jinja {{env.HOME}}/.config/databases/{{this.DB_NAME}}"
```

> **NOTE**: Older versions of Dynaconf used the `@casting` prefixes for env vars like `export DYNACONF_INTEGER='@int 123'` still works but this casting is deprecated in favor of using TOML syntax described above. To disable the `@casting` do `export AUTO_CAST_FOR_DYNACONF=false`

## Merging new data to existing variables

### Nested keys in dictionaries via environment variables.

> **New in 2.1.0**
> 
> This is useful for `Django` settings.

Lets say you have a configuration like this:

`settings.py`

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'module.foo.engine',
        'ARGS': {'timeout': 30}
    }
}
```

And  now you want to change the values of `ENGINE` to `other.module`, via environment variables you can use the format `${ENVVAR_PREFIX}_${VARIABLE}__${NESTED_ITEM}__${NESTED_ITEM}`

Each `__` (dunder, a.k.a *double underline*) denotes access to nested elements in a dictionary.

So 

```py
DATABASES['default']['ENGINE'] = 'other.module'
```

Can be expressed as environment variables as:

```bash
export DYNACONF_DATABASES__default__ENGINE=other.module
```

> **NOTE**: if you are using Django extension then the prefix will be `DJANGO_` instead of `DYNACONF_` and the same if you are using `FLASK_` or a custom prefix if you have customized the `ENVVAR_PREFIX`.

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'timeout': 30}
    }
}
```

> **IMPORTANT** lower case keys are respected only on *nix systems, unfortunately Windows environment variables are case insensitive and Python reads it as all upper cases, that means that if you are running on Windows the dictionary can have only upper case keys.

Now if you want to add a new item to `ARGS` key:

```bash
export DYNACONF_DATABASES__default__ARGS__retries=10
```

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'timeout': 30, 'retries': 10}
    }
}
```

and you can also pass a `toml` like dictionary to be merged with existing `ARGS` key using `@merge` token.

> **new in 3.0.0**

```bash
# as a toml (recommended)
export DYNACONF_DATABASES__default__ARGS='@merge {timeout=50, size=1}'
# OR as a json
export DYNACONF_DATABASES__default__ARGS='@merge {"timeout": 50, "size": 1}'
# OR as plain key pair
export DYNACONF_DATABASES__default__ARGS='@merge timeout=50,size=1'
```

will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'retries': 10, 'timeout': 50, 'size': 1}
    }
}
```

Now if you want to clean an existing nested attribute you can just assign the new value.

```bash
# As a TOML empty dictionary `"{}"`
export DYNACONF_DATABASES__default__ARGS='{}'
```

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {}
    }
}
```

```bash
# As a TOML  dictionary (recommended)
export DYNACONF_DATABASES__default__ARGS='{timeout=90}'
```

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'timeout': 90}
    }
}
```

And if in any case you need to completely remove that key from the dictionary:

```bash
export DYNACONF_DATABASES__default__ARGS='@del'
```

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module'
    }
}
```

### Using the `dynaconf_merge` mark on configuration files.

> **New in 2.0.0**

To merge exported variables there is the **dynaconf_merge** tokens, example:

Your main settings file (e.g `settings.toml`) has an existing `DATABASE` dict setting on `[default]` env.

Now you want to contribute to the same `DATABASE` key by adding new keys, so you can use `dynaconf_merge` at the end of your dict:

In specific `[envs]`

```cfg
[default]
database = {host="server.com", user="default"}

[development]
database = {user="dev_user", dynaconf_merge=true}
```

or

> New in **2.2.0**

```cfg
[default]
database = {host="server.com", user="default"}

[development.database]
dynaconf_merge = {user="dev_user"}
```

In an environment variable use `@merge` token:

> **New in 2.2.0**

```bash
# Toml formatted envvar
export DYNACONF_DATABASE='@merge {password=1234}'
```

or `dunder` (recommended)

```bash
# Toml formatted envvar
export DYNACONF_DATABASE__PASSWORD=1234
```

The end result will be on `[development]` env:

```python
settings.DATABASE == {'host': 'server.com', 'user': 'dev_user', 'password': 1234}
```

Read more in [Getting Started Guide](usage.html#merging-existing-values)

### The global prefix

The **DYNACONF_{param}** prefix is set by **ENVVAR_PREFIX_FOR_DYNACONF** and serves only to be used in environment variables to override config values.

This prefix itself can be changed to something more significant for your application, however we recommend keeping **DYNACONF_{param}** as your global env prefix.

Setting **ENVVAR_PREFIX_FOR_DYNACONF** to `false` will disable the prefix entirely and cause Dynaconf to load *all* environment variables. When providing `ENVVAR_PREFIX_FOR_DYNACONF` as parameter to **LazySettings** or **settings.configure**, make sure to give it a Python-native `False`:

```python
from dynaconf import LazySettings
settings = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF=False)
```

> **NOTE**: See the [Configuring dynaconf](configuration.html) section in documentation to learn more on how to use `.env` variables to configure dynaconf behavior.
