# Environment variables

## overloading parameters via env vars

All configuration parameters, including **custom** environments and [dynaconf configuration](configuration.html), can be overridden through environment variables.

To override the configuration parameter **{param}**, use an environment variable named **DYNACONF_{PARAM}**. For instance, to override the **"HOST"** configuration parameter, you can run your application with:

```bash
DYNACONF_HOST='otherhost.com' python yourapp.py
```

## .env files

If you don't want to declare the variables on every program call you can run `export DYNACONF_{PARAM}` in your shell or put the values in a `.env` file located in the same directory as your settings files (the root directory of your application), variables in `.env` does not overrride existing environment variables.

> **IMPORTANT**: Dynaconf will search for a `.env` located in the root directory of your application, if not found it will continue searching in parent directories until it reaches the root. To avoid conflicts we recommend to have a `.env` even if it is empty.

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

### The global prefix

The **DYNACONF_{param}** prefix is set by **GLOBAL_ENV_FOR_DYNACONF** and serves only to be used in environment variables to override config values.

This prefix itself can be changed to something more significant for your application, however we recommend kepping **DYNACONF_{param}** as your global env prefix.

> **NOTE**: See the [Configuring dynaconf](configuration.html) section in documentation to learn more on how to use `.env` variables to configure dynaconf behavior.
