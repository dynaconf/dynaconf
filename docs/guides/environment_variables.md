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

```
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
DYNACONF_ARRAY=[1, 2, 3]
DYNACONF_ARRAY=[1.1, 2.2, 3.3]
DYNACONF_ARRAY=['a', 'b', 'c']

# Dictionaries
DYNACONF_DICT={key="abc",val=123}

# toml syntax does not allow `None/null` values so use @none
DYNACONF_NONE='@none None'

# toml syntax does not allow mixed type arrays so use @json
DYNACONF_ARRAY='@json [42, 3.14, "hello", true, ["otherarray"], {"foo": "bar"}]'
```

> **NOTE**: Older versions of Dynaconf used the `@casting` prefixes for env vars like `export DYNACONF_INTEGER='@int 123'` still works but this casting is deprecated in favor of using TOML syntax described above. To disable the `@casting` do `export AUTO_CAST_FOR_DYNACONF=false`

### Merging exported variables with existing data

> **New in 2.0.0**

To merge exported variables there is the **dynaconf_merge** tokens, example:

Your main settings file (e.g `settings.toml`) has an existing `DATABASE` dict setting on `[default]` env.

Now you want to contribute to the same `DATABASE` key by addind new keys, so you can use `dynaconf_merge` at the end of your dict:

In specific `[envs]`

```toml
[default]
database = {host="server.com", user="default"}

[development]
database = {user="dev_user", dynaconf_merge=true}
```

In an environment variable:

```bash
# Toml formatted envvar
export DYNACONF_DATABASE='{password=1234, dynaconf_merge=true}'
```

The end result will be on `[development]` env:

```python
settings.DATABASE == {'host': 'server.com', 'user': 'dev_user', 'password': 1234}
```

Read more in [Getting Started Guide](usage.html)

### The global prefix

The **DYNACONF_{param}** prefix is set by **GLOBAL_ENV_FOR_DYNACONF** and serves only to be used in environment variables to override config values.

This prefix itself can be changed to something more significant for your application, however we recommend keeping **DYNACONF_{param}** as your global env prefix.

Setting **GLOBAL_ENV_FOR_DYNACONF** to `false` will disable the prefix entirely and cause Dynaconf to load *all* environment variables. When providing `GLOBAL_ENV_FOR_DYNACONF` as parameter to **LazySettings** or **settings.configure**, make sure to give it a Python-native `False`:

```python
from dynaconf import LazySettings
settings = LazySettings(GLOBAL_ENV_FOR_DYNACONF=False)
```

> **NOTE**: See the [Configuring dynaconf](configuration.html) section in documentation to learn more on how to use `.env` variables to configure dynaconf behavior.
