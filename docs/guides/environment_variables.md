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

### Merging exported variables with existing data

When you have existing variables of type dict or list and you want to contribute to existing data instead of overriding
it is possible to use the special `@merge` notation.

#### Examples:

##### There is already a list defined in settings and you want to add items to the same list.

Existing `settings.toml`
```toml
[default]
colors = ['yellow', 'blue', 'red']
```

Now you want to add `green` color to that existing list via environment variable:

```bash
export DYNACONF_COLORS="@merge ['green']"
```

When you access the variable you will get:

```py
from dynaconf import settings
assert settings.COLORS == ['green', 'yellow', 'blue', 'red']
```

But, what if green was already on the list? Dynaconf default behavior is to duplicate it like:

```toml
[default]
colors = ['yellow', 'blue', 'red', 'green']
```
```bash
export DYNACONF_COLORS="@merge ['green']"
```
```py
assert settings.COLORS == ['green', 'yellow', 'blue', 'red', 'green']
```

See the double `green`? how to avoid that? use **@merge_unique** which will not allow duplicated items, it will remove the duplicate from the existing list and add the new one in the new defined order.

```bash
export DYNACONF_COLORS="@merge_unique ['green']"
```
```py
assert settings.COLORS == ['yellow', 'blue', 'red', 'green']
```

The **@merge** also works for dictionaries:

```toml
[default]
database = {host="server.com", user="admin"}
```
```bash
export DYNACONF_DATABASE='@merge {password="s3cr4t"}'
```
```py
assert settings.DATABASE == {'host': 'server.com', 'user': 'admin', 'password': 's3cr4t'}
```

> NOTE: for dictionaries `@merge_unique` does not have any effect as it will by default exclude existing duplicate keys and replace with the newer ones.

#### Known caveats

The merge functionality works only for the **first** level keys on a dictionary and only **first** level items on a list.

In other words:

if I do `export DYNACONF_COLORS='@merge ["blue", "red", "green"]'`

```yaml
default:
  colors:
    - yellow
```

the exported variable will work and will merge to `colors` because it is the first level list on the `default` env and `settings.COLORS` is now `["blue", "red", "green", "yellow"]`.

However if I do if I do `export DYNACONF_COLORS='@merge {basic=["blue", "red", "green"]}'`

```yaml
default:
  colors:
    basic:
      - yellow
    compound:
      - fucsia
```

Now it is not merging the nested elements and you loose existing `yellow` value having `settings.BASIC.colors` as `["blue", "red", "green"]` and you kept `settings.COLORS.compound` unchanged.

### The global prefix

The **DYNACONF_{param}** prefix is set by **GLOBAL_ENV_FOR_DYNACONF** and serves only to be used in environment variables to override config values.

This prefix itself can be changed to something more significant for your application, however we recommend kepping **DYNACONF_{param}** as your global env prefix.

> **NOTE**: See the [Configuring dynaconf](configuration.html) section in documentation to learn more on how to use `.env` variables to configure dynaconf behavior.
