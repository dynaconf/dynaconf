# Validation

Dynaconf allows the validation of settings parameters, in some cases you may want to validate the settings before starting the program.

Lets say you have `settings.toml`

```ini
[default]
version = "1.0.0"
age = 35
name = "Bruno"
DEV_SERVERS = ['127.0.0.1', 'localhost', 'development.com']
PORT = 8001

[production]
PROJECT = "This is not hello_world"
```

## Validating in Python programmatically

At any point of your program you can do:

```python
from dynaconf import Dynaconf, Validator


settings = Dynaconf(
    validators=[
        # Ensure some parameters exists (are required)
        Validator('VERSION', 'AGE', 'NAME', must_exist=True),

        # Ensure some password cannot exist
        Validator('PASSWORD', must_exist=False),

        # Ensure some parameter mets a condition
        # conditions: (eq, ne, lt, gt, lte, gte, identity, is_type_of, is_in, is_not_in)
        Validator('AGE', lte=30, gte=10),

        # validate a value is eq in specific env
        Validator('PROJECT', eq='hello_world', env='production'),

        # Ensure some parameter (string) meets a condition
        # conditions: (len_eq, len_ne, len_min, len_max, cont)
        # Determines the minimum and maximum length for the value
        Validator("NAME", len_min=3, len_max=125),

        # Signifies the presence of the value in a set, text or word
        Validator("DEV_SERVERS", cont='localhost'),

        # Checks whether the length is the same as defined.
        Validator("PORT", len_eq=4),
    ]
)
```

The above will raise `dynaconf.validators.ValidationError("AGE must be lte=30 but it is 35 in env DEVELOPMENT")` and `dynaconf.validators.ValidationError("PROJECT must be eq='hello_world' but it is 'This is not hello_world' in env PRODUCTION")`


### Providing default or computed values


Validators can be used to provide default or computed values.

#### Default values

```py
Validator("FOO", default="A default value for foo")
```

Then if not able to load the values from files or environment this default value will be set for that key.


#### Computed values

Sometimes you need some values to be computed by calling functions, just pass a callable to the `default` argument.

```py

Validator("FOO", default=my_function)

```

then

```py

def my_function(settings, validator):
    return "this is computed during validation time"

```

If you want to be lazily evaluated, `my_function` has to be redefined as

```py
def my_lazy_function(value, **context):
    """
    value: Default value passed to the validator, defaults to `empty`
    context: A dictionary containing
            env: All the environment variables
            this: The settings instance
    """
    return "When the first value is accessed, then the my_lazy_function will be called"
```

Subsequently

```py
from dynaconf.utils.functional import empty
from dynaconf.utils.parse_conf import Lazy

Validator("FOO", default=Lazy(empty, formatter=my_lazy_function))

```

You can also use dot-delimited paths for registering validators on nested structures:

```python
# Register validators
settings.validators.register(

    # Ensure the database.host field exists.
    Validator('DATABASE.HOST', must_exist=True),

    # Make the database.password field optional. This is a default behavior.
    Validator('DATABASE.PASSWORD', must_exist=None),
)

# Fire the validator
settings.validators.validate()
```

### Combining validators

Validators can be combined using:


#### `|` **or** operator.

```py
Validator('DATABASE.USER', must_exist=True) | Validator('DATABASE.KEY', must_exist=True)
```

#### `&` **and** operator.

```py
Validator('DATABASE.HOST', must_exist=True) & Validator('DATABASE.CONN', must_exist=True)
```

## CLI and dynaconf_validators.toml

It is possible to define validators in **TOML** file called **dynaconf_validators.toml** placed in the same folder as your settings files.

`dynaconf_validators.toml` equivalent to program above

```ini
[default]

version = {must_exist=true}
name = {must_exist=true}
password = {must_exist=false}

# dot notation is also supported
'a_big_dict.nested_1.nested_2.nested_3.nested_4' = {must_exist=true, eq=1}

  [default.age]
  must_exist = true
  lte = 30
  gte = 10

[production]
project = {eq="hello_world"}
```

Then to fire the validation use:

```bash
$ dynaconf validate
```

This returns code 0 (success) if validation is ok.


!!! info
    All values in dynaconf are parsed using toml format, TOML tries to be smart
    and infer the type of the settings variables, some variables will be automatically
    converted to integer:

    ```
    FOO = "0x..."  # hexadecimal
    FOO = "0o..."  # Octal
    FOO = "0b..."  # Binary
    ```

    All cases are on toml specs https://github.com/toml-lang/toml/blob/master/toml.abnf

    If you need to force a specific type casting there are 2 options.

    1. Use double quoted for strings ex: `FOO = "'0x...'"  will be string.
    2. Specify the type using `@`  ex: FOO = "@str 0x..."
       (available converters are `@int, @float, @bool, @json`)

## Selective Validation

> **New in 3.1.6**

You can also choose what sections of the settings you do or don't want to validate.
This is useful when:

 - You want to add additional validators after the settings object is created.
 - You want settings validated only when certain sections of your project are loaded.
 - You want to offer incremental configuration levels, validating only what is needed.

Selective validation can be performed both when creating a settings object and when calling validate on a settings object's validators. The new arguments accept either a string representing a settings path or a list of strings representing settings paths.

A settings path starts at the top level element and can be specified down to the lowest component. For example: `my_settings.server.user.password` can have the following settings paths passed in `server`, `server.user`, `server.user.password`.

*Note:* Selective validation matches the passed in value(s) to settings paths that start with that value. This means that passing `exclude="FOO"` will exclude not only paths that start with `FOO` but also `FOOBAR`.

Examples:

**-- config.py --**
```python
...
# create a settings object, validating only settings under settings.server
settings = Dynaconf(
    validators=[
        Validator(
            "server.hostname",
            "server.port",
            "server.auth",
            must_exist=True
        ),
        Validator(
            "module1.value1",
            "module1.value2",
            "module1.value3",
            must_exist=True
        ),
        Validator(
            "module2.value1",
            "module2.value2",
            "module2.bad",
            must_exist=True
        )
    ],
    validate_only="server"
)
```

**-- module1.py --**
```python
...
# call validation on module1 settings
settings.validators.validate(only=["module1"])
```

**-- module2.py --**
```python
...
# call validation on module2 settings
# ignore validation for a subsection of module2's settings
settings.validators.validate(
    only=["module2"],
    exclude=["module2.bad"]
)
```

> **Validate only current env**

You can specify if you want to validate all environments defined for a validator (default behavior) or only the current environement. In the first case, the validators will run on all possible settings defined in their list of environment, while in the latter the validators with environments different from the current environment will be skipped.

This is useful when your configuration for different environments (let's say `production` and `development`) comes from different files you don't necesseraly have access to during development. You would want to write different validators for your `development` and `production` environments, and only run the right validator for the current environment.

Here is an example of the option using:

- `settings.toml`
```ini
[development]
version = "dev"
age = 35
name = "Bruno"
servers = ['127.0.0.1', 'localhost', 'development.com']
PORT = 80

[production]
version = "1.0.0"
age = 35
name = "Bruno"
servers = ['production.com']
PORT = 443
```

- `.secrets.toml`
```ini
[production]
api_key = 'secret_api_key'
```

You could then have these validators:

```python
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    settings_files=['setting.toml', '.secrets.toml'],
    environments=True,
    validators=[
        # Ensure some parameters exists for both envs
        Validator('VERSION', 'NAME', 'SERVERS', envs=['development', 'production'], must_exist=True),

        # Ensure some parameter validate certain condition in dev env
        Validator("SERVERS", env='development', cont='localhost'),

        # Ensure some parameter exists in production env
        Validator('API_KEY', env='production', must_exist=True),
    ]
)
```
And suppose during development, when `settings.current_env == 'development'`, you don't have the file `.secrets.toml`.

Running `settings.validators.validate()` will fail even if `settings.current_env == 'development'`, because by default all validators will run on all of their environments, whether or not it is the current env. However you could create your settings with the parameter `validate_only_current_env=True`, and nothing will be raised if `settings.current_env == 'development'`. Still, if `settings.current_env == 'production'`, it will fail, forcing you to have `.secrets.toml` file in the directory in `production`, but not necessarily during `development`.
