# Environment Variables

Dynaconf prioritizes environment variables over files as the best recommendation to keep your settings.

According to [12factorapp](https://12factor.net) it is a good practice to keep your configurations based on environment.

In addition to that Dynaconf offers some approaches you may want to **Optionally** follow:

- Add a list of validators to `validators=[Validator()]` on your dynaconf settings instance and provide [defaults and constraints](validation.md).
- Enable `load_dotenv` and provide a `.env.example` or `.env` file with the default variables.
- Write your variables in a [settings file](settings_files.md) in the format of your choice.
- Load your settings from [vault or redis](secrets.md)

## Environment variables

You can override any setting key by exporting an environment variable prefixed by `DYNACONF_` (or by the [custom prefix](configuration.md/#envvar_prefix)).

!!! warning
    Dynaconf will only look for UPPERCASE prefixed envvars. This means envvar exported as `dynaconf_value` or `myprefix_value` won't be loaded, while `DYNACONF_VALUE` and `MYPREFIX_VALUE` (when proper set) will.

### Example

Notice that when loading environment variables, dynaconf will parse the value using `toml` language so it will try to automatically convert to the proper data type.

```bash
export DYNACONF_NAME=Bruno                                   # str: "Bruno"
export DYNACONF_NUM=42                                       # int: 42
export DYNACONF_AMOUNT=65.6                                  # float: 65.6
export DYNACONF_THING_ENABLED=false                          # bool: False
export DYNACONF_COLORS="['red', 'gren', 'blue']"             # list: ['red', 'gren', 'blue']
export DYNACONF_PERSON="{name='Bruno', email='foo@bar.com'}" # dict: {"name": "Bruno", ...}
export DYNACONF_STRING_NUM="'76'"                            # str: "76"
export DYNACONF_PERSON__IS_ADMIN=true                        # bool: True (nested)
```

!!! info
    For envvars Dynaconf will automatically transform `True` and `False` to `true` and `false` respectively,
    this transformation allows TOML to parse the value as a boolean.
    If you want to keep the original value in this case use `@str` or wrap it in quotes twice like `FOO='"True"'`
    Note that this applies only for strictly string equal to `True|False` doesn't apply to same string found
    inside toml data structures.

With the above it is now possible to read the settings in your `program.py` using:

```python
from dynaconf import Dynaconf

settings = Dynaconf()

assert settings.NAME == "Bruno"
assert settings.num == 42
assert settings.amount == 65.6
assert settings['thing_enabled'] is False
assert 'red' in settings.get('colors')
assert settings.person.email == "foo@bar.com"
assert settings.person.is_admin is True
assert settings.STRING_NUM == "76"
```

!!! tip
    Dynaconf has multiple valid ways to access settings keys so it is compatible with your
    existing settings solution. You can access using `.notation`, `[item] indexing`, `.get method`
    and also it allows `.notation.nested` for data structures like dicts.
    **Also variable access is case insensitive for the first level key**

!!! warning
    When exporting data structures such as `dict` and `list` you have to use one of:
    ```
    export DYNACONF_TOML_DICT={key="value"}
    export DYNACONF_TOML_LIST=["item"]
    export DYNACONF_JSON_DICT='@json {"key": "value"}'
    export DYNACONF_JSON_LIST='@json ["item"]'
    ```
    Those 2 ways are the only ways for dynaconf to load `dicts` and `lists` from envvars.

## Custom Prefix

You are allowed to customize the prefix for your env vars. Let's say your application
is called "PEANUT"

```bash
export PEANUT_USER=admin
export PEANUT_PASSWD=1234
export PEANUT_DB={name='foo', port=2000}
export PEANUT_DB__SCHEME=main
```

Now to your settings instance you can customize the prefix:

```py
from dynaconf import Dynaconf

settings = Dynaconf(envvar_prefix="PEANUT")


assert settings.USER == "admin"
assert settings.PASSWD == 1234
assert settings.db.name == "foo"
assert settings.db.port == 2000
assert settings.db.scheme == 'main'
```

If you don't want to use any prefix (load unprefixed variables) the correct
way is to set it like so:
```py
from dynaconf import Dynaconf

settings = Dynaconf(envvar_prefix=False)
```

## Dot env

When you have multiple environment variables to set it is useful to automate the definition
and Dynaconf comes with `Python-Dotenv` support.

You can put in the root of your application a file called **.env**

```bash
DYNACONF_USER=admin
```

Then pass `load_dotenv=True` to your settings.

```py
from dynaconf import Dynaconf

settings = Dynaconf(load_dotenv=True)

assert settings.USER == "admin"
```

## Type Casting and Lazy Values

In addition to `toml` parser you can also force your variables to be converted
in to a desired data type.

```bash
export PREFIX_NONE='@none None'                        # None
export PREFIX_NONE='@int 16'                           # int: 16
export PREFIX_NONE='@bool off'                         # bool: False
export PREFIX_ARRAY='@json [42, "Oi", {"foo": "bar"}]' # Heterogeneus list
```

### Lazy Values

Dynaconf support 2 types of lazy values `format` and `jinja` which allows
template substitutions.

```bash
export PREFIX_PATH='@format {env[HOME]}/.config/{this.DB_NAME}'
export PREFIX_PATH='@jinja {{env.HOME}}/.config/{{this.DB_NAME}} | abspath'
```

### Adding a Custom Casting Token

If you would like to add a custom casting token, you can do so by adding a
converter. For example, if we would like to cast strings to a pathlib.Path
object we can add in our python code:

```python
# app.py
from pathlib import Path
from dynaconf import add_converter

add_converter("path", Path)
```

In the settings file we can now use the @path casting token. Like with other
casting tokens you can also combine them:

```toml
# settings.toml
my_path = "@path /home/foo/example.txt"
parent = "@path @format {env[HOME]}/parent"
child = "@path @format {this.parent}/child"
```


## Environment variables filtering

All environment variables (naturally, accounting for prefix rules) will be
used and pulled into the settings space.

You can change that behaviour by enabling the filtering of unknown environment
variables:

```py
from dynaconf import Dynaconf

settings = Dynaconf(ignore_unknown_envvars=True)
```

In that case, only previously defined variables (e.g. specified in
`settings_file`/`settings_files`, `preload` or `includes`) will be loaded
from the environment. This way your setting space can avoid pollution
or potentially loading of sensitive information.
