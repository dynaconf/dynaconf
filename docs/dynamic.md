## Template substitutions

Dynaconf has 2 tokens to enable string substitutions, the interpolation works with `@format` and `@jinja`.

### @format token

Dynaconf allows template substitutions for strings values, by using the `@format` token prefix and including placeholders accepted by Python's `str.format` method Dynaconf will call
it lazily upon access time.

The call will be like:

```py
"<YOURVALUE>".format(env=os.environ, this=dynaconf.settings)
```

So in your string you can refer to environment variables via `env` object, and also to variables defined int the settings object itself via `this` reference. It is lazily evaluated on access it will use the final value for a settings regardless the order of load.

Example:

```bash
export PROGRAM_NAME=calculator
```

settings.toml

```toml
[default]
DB_NAME = "mydb.db"

[development]
DB_PATH = "@format {env[HOME]}/{this.current_env}/{env[PROGRAM_NAME]}/{this.DB_NAME}"
```

- `{env[HOME]}` is the same as `os.environ["HOME"]` or `$HOME` in the shell.
- `{this.current_env}` is the same as `settings.current_env`
- `{env[PROGRAM_NAME]}` is the same as `os.environ["PROGRAM_NAME"]` or `$PROGRAM_NAME` in the shell.
- `{this.DB_NAME}` is the same as `settings.DB_NAME` or `settings["DB_NAME"]`

so in your `program`

```py
from dynaconf import settings

settings.DB_PATH == '~/DEVELOPMENT/calculator/mydb.db'
```

`@format` token can be used together with tokens like `@str`, `@int`, `@float`, `@bool`, and `@json` to cast the results parsed by `@format`.

Example: 

Casting to integer from `@format` templated values

```yaml
NUM_GPUS: 4
# This returns the integer after parsing
FOO_INT: "@int @format {this.NUM_GPUS}"
# This returns the string after parsing
FOO_STR: "@format {this.NUM_GPUS}"
```

### @jinja token

If `jinja2` package is installed then dynaconf will also allow the use jinja to render string values.

Example:

```bash
export PROGRAM_NAME=calculator
```

settings.toml

```toml
[default]
DB_NAME = "mydb.db"

[development]
DB_PATH = "@jinja {{env.HOME}}/{{this.current_env | lower}}/{{env['PROGRAM_NAME']}}/{{this.DB_NAME}}"
```

so in your `program`

```py
from dynaconf import settings

settings.DB_PATH == '~/development/calculator/mydb.db'
```

The main difference is that Jinja allows some Python expressions to be evaluated such as `{% for, if, while %}` and also supports calling methods and has lots of filters like `| lower`.

Jinja supports its built-in filters listed in [Builtin Filters Page](http://jinja.palletsprojects.com/en/master/templates/#builtin-filters) and Dynaconf includes additional filters for `os.path` module: `abspath`. `realpath`, `relpath`, `basename` and `dirname` and usage is like: `VALUE = "@jinja {{this.FOO | abspath}}"`

`@jinja` token can be used together with tokens like `@str`, `@int`, `@float`, `@bool`, and `@json` to cast the results parsed by `@jinja`.

Example:

Casting to integer from `@jinja` templated values

```yaml
NUM_GPUS: 4
# This returns the integer after parsing
FOO_INT: "@int @jinja {{ this.NUM_GPUS }}"
# This returns the string after parsing
FOO_STR: "@jinja {{ this.NUM_GPUS }}"
```

Example:

Casting to a `json` dict from `@jinja` templated values

```yaml
MODEL_1:
  MODEL_PATH: "src.main.models.CNNModel"
  GPU_COUNT: 4
  OPTIMIZER_KWARGS:
    learning_rate: 0.002

MODEL_2:
  MODEL_PATH: "src.main.models.VGGModel"
  GPU_COUNT: 2
  OPTIMIZER_KWARGS:
    learning_rate: 0.001

# Flag to choose which model to use
MODEL_TYPE: "MODEL_2"

# This returns the dict loaded from the resulting json
MODEL_SETTINGS_DICT: "@json @jinja {{ this|attr(this.MODEL_TYPE) }}"

# This returns the raw json string
MODEL_SETTINGS_STR: "@jinja {{ this|attr(this.MODEL_TYPE) }}"
```


## Name aliasing

In certain cases you need to reuse some variable value respecting the exact 
data type it is previously defined in another step of the settings load.

Example:

```py title="config.py"
from dynaconf import Dynaconf
settings = Dynaconf(settings_files=["settings.toml", "other.toml"])  
```

```toml title="settings.toml"
thing = "value"
number = 42
```

```toml title="other.toml"
other_thing = "@get thing"

# providing default if thing is undefined
other_thing = "@get thing 'default value'"

## type casting
# Ensure the aliased value is of type int
other_number = "@get number @int"

# Ensure type and provide default if number is undefined
other_number = "@get number @int 12"
```

The `@get` is lazily evaluated and subject to `DynaconfFormatError` in case of
malformed expression, it is recommended to add validators.


## Access Hooks

Dynaconf supports access hooks, which allow the user to register functions that
will be called each time a variable is accessed on a `Dynaconf` instance.

This feature is useful to load settings from external sources, such as from
cloud provider's secrets managers, or when you need special processing on top
of raw values (such as decrypting an encrypted value).

NOTES:

- You must define the logic of each hook, dynaconf just calls it
- You must take care of caching and caching invalidation
- This may introduce overhead dependending on how the hook function is
    implemented

To register an access hook, you need to wrap the `Dynaconf` instance with
`HookableSettings` and pass a `Action` to `Hook` mapping in to the constructor
in the `_registered_hooks` kwarg. For example,

```python
# So you have a function that retrieves data from external source

CACHE = {}  # could be Redis

def get_data_from_somewhere(settings, result, key, *args, **kwargs):
    """Your function that goes to external service like gcp, aws, vault, etc

    Parameters:
        settings: A copy of settings, changes made are valid only during the
            scope of this function.
        result: The object that holds the setting known to Dynaconf at the
            moment of access in the .value attribute.
        key: The accessed key just as passed to Dynaconf.get, usually a
            single str, but if the requested key was dotted then the whole
            path is passed to this function.
        *args and **kwargs: extra positional or named arguments passed to .get
            such as default,cast,fresh,parent etc.
    """
    if key in CACHE:
        return CACHE[key]

    # Assuming result.value is '@special:/foo/bar:token'
    if isinstance(result.value, str) and result.value.startswith("@special:"):
        _, path, identifier = result.value.split(":")
        # value = get_value_from_special_place(path, identifier)
        value = CACHE[key] = "lets believe it was retrieved from special place"
        return value

    return result

# ---

from dynaconf import Dynaconf
from dynaconf.hooking import HookableSettings, Hook, Action

# Create a Dynaconf instance
settings = Dynaconf(
    # set the Hookable wrapper class
    _wrapper_class=HookableSettings,
    # Register your hooks, see the Action enum for available values
    # you can have multiple hooks, value passes from one to another
    _registered_hooks={
       Action.AFTER_GET: [Hook(get_data_from_somewhere)]
    },
)

# this value can actually come from settings files or envvars
settings.set("token", "@special:/vault/path:token")

assert settings.token == "lets believe it was retrieved from special place"

# from cache this time
assert settings.token == "lets believe it was retrieved from special place"
```

### Merging with access hooks

When the `result.value` is a mergeable data structure like `dict` or `list`
and you want the merging to be applied, then the hook must delegate the merging
to the given `settings` by `set`ing the result (which will perform the merging)
and returning the result of `get`ing the setting from the given `settings`.

```py
def get_data_from_somewhere(settings, result, key, *args, **kwargs):
    """Your function that goes to external service like gcp, aws, vault, etc
    NOTE: settings in this context is copy of settings, changes made are
    valid only during the scope of this function.
    """
    if key in CACHE:
        return CACHE[key]

    ...

    interesting_keys = ["foo", "bar", "zaz"]  # known to be dicts or lists
    if key in interesting_keys:
      value = CACHE[key] = get_value_from_special_place(key)
      settings.set(key, value)  # process merging and parsing
      return settings.get(key, result.value)

    return result
```


### Registering Hooks After Dynaconf is instantiated

It is ok to register hooks later, which might be useful to do it conditionally.


```py
if something:
    settings.set("_registered_hooks", {Action.AFTER_GET: [Hook(....)]})
```

It also works if you use `dynaconf_hooks.py` to register it conditionally.

```py
# dynaconf_hooks.py
def post(settings):
    data = {}
    if settings.something:
        data["_registered_hooks"] = {Action.AFTER_GET: [Hook(....)]}
    return data
```
