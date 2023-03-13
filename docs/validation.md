# Validation

Dynaconf allows the validation of settings parameters, in some cases you may want to validate the settings before starting the program.

Let's say you have `settings.toml`

```ini
[default]
version = "1.0.0"
age = 35
name = "Bruno"
DEV_SERVERS = ['127.0.0.1', 'localhost', 'development.com']
PORT = 8001
JAVA_BIN = "/usr/bin/java"

[production]
PROJECT = "This is not hello_world"
```

## Validating in Python programmatically

At any point of your program you can do:

```python
from pathlib import Path
from dynaconf import Dynaconf, Validator


settings = Dynaconf(
    validators=[
        # Ensure some parameters exist (are required)
        Validator('VERSION', 'AGE', 'NAME', must_exist=True),

        # Ensure some password cannot exist
        Validator('PASSWORD', must_exist=False),

        # Ensure some parameter meets a condition
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

        # Ensure java_bin is returned as a Path instance
        Validator("JAVA_BIN", must_exist=True, cast=Path),

        # Ensure a value meets a condition specified by a callable 
        Validator("VERSION", must_exist=True, condition=lambda v: v.startswith("1.")),
    ]
)
```

The above will raise `dynaconf.validators.ValidationError("AGE must be lte=30 but it is 35 in env DEVELOPMENT")` and `dynaconf.validators.ValidationError("PROJECT must be eq='hello_world' but it is 'This is not hello_world' in env PRODUCTION")`


## Validator parameters 

Validators can be created by passing the following arguments: 

```python
# names: list[str]
# can be a single or multiple positional strings 
Validator('VERSION', 'AGE', 'NAME'),
# can also use dot notation 
Validator('DATABASE.HOST', 'DATABASE.PORT'),
Validator('DATABASE.HOST', 'DATABASE.PORT'),


# must_exist: bool (alias: required)
# Check whether variable must or not exist 
Validator('VERSION', must_exist=True), 
Validator('PASSWORD', must_exist=False),
# there is an alias for must_exist called `required`
Validator('VERSION', required=True), 

# condition: callable 
# A function or any other callable that accepts `value` and 
# must return a boolean 
Validator('VERSION', condition=lambda v: v.startswith("1.")),

# when: Validator
# Condtionally runs the validator only when the passed validator passes
Validator(
    'VERSION',
    condition=lambda v: v.endswith("-dev"),
    when=Validator('ENV_FOR_DYNACONF', eq='development')
),

# env: str 
# Runs the validator against the specified env, only for 
# settings that are loaded from files with environments=True 
Validator('VERSION', must_exist=True, env='production'),

# messages: dict[str, str]
# A dictionary with custom messages for each validation type 
Validator(
    "VERSION", 
    must_exist=True,
    condition=lambda v: v.startswith("1."),
    messages={
        "must_exist_true": "You forgot to set {name} in your settings.",
        "condition": "The allowed version must start with 1., you passed {value}"
    }
),

# cast: callable/class 
# A type or a callable to transform the type of the passed object
# can also be used to apply transformations/normalizations
Validator("VERSION", cast=str),
Validator("VERSION", cast=lambda v: v.replace("1.", "2.")),
Validator("STATIC_FOLDER", cast=Path)
# Cast will be called for default values and also for values defined on 
# settings via files or envvars

# default: any value or a callable 
# If the value is not found it will be set to the default value 
# if the default is a callable it will be called with the
# settings and instance of validator as arguments.
def default_connection_args(settings, validator):
    if settings.DATABASE.uri.startswith("sqlite://"):
        return {"echo": True}
    else:
        return {}

Validator("DATABASE.CONNECTION_ARGS", default=default_connection_args), 
# default will be called only if the value is not explicitly set on settings 
# via files or env vars.

# description: str
# As of 3.1.12 dynaconf doesn't use this for anything 
# but there are plugins and external tools that uses it.
# this value to generate documentation 
Validator("VERSION", description="The version of the app"),

# apply_default_on_none: bool 
# YAML parser parses empty values as `None` so in this case
# you might want to force the application of default when the 
# value in settings is `None`
Validator("VERSION", default="1.0.0", apply_default_on_none=True),


# Operations: comparison operations 
# - eq: value == other
# - ne: value != other
# - gt: value > other
# - lt: value < other
# - gte: value >= other
# - lte: value <= other
# - is_type_of: isinstance(value, type)
# - is_in:  value in sequence
# - is_not_in: value not in sequence
# - identity: value is other
# - cont: contain value in
# - len_eq: len(value) == other
# - len_ne: len(value) != other
# - len_min: len(value) > other
# - len_max: len(value) < other
# - startswith: value.startswith(other) 
# - endswith: value.endswith(other)
# Examples:
Validator("VERSION", eq="1.0.0"),
Validator("VERSION", ne="1.0.0"),
Validator("AGE", gt=18),
Validator("AGE", lt=18),
Validator("AGE", gte=18),
Validator("AGE", lte=18),
Validator("AGE", is_type_of=int),
Validator("AGE", is_in=[18, 19, 20]),
Validator("AGE", is_not_in=[18, 19, 20]),
Validator("THING", identity=thing),  # settings.THING is thing
Validator("THING", cont="hello"),  # "hello" in settings.THING
Validator("THING", len_eq=3),  # len(settings.THING) == 3
Validator("THING", len_ne=3),  # len(settings.THING) != 3
Validator("THING", len_min=3),  # len(settings.THING) > 3
Validator("THING", len_max=3),  # len(settings.THING) < 3
Validator("THING", startswith="hello"),  # settings.THING.startswith("hello")
Validator("THING", endswith="world"),  # settings.THING.endswith("world")
```

## Complex validators 

A single validator can have multiple conditions.

```python
Validator(
  "NAME",
  ne="john",
  len_min=4,
  must_exist=True, # redundant but allowed 
  startswith="user_",
  cast=str,
  condition=lambda v: v not in FORBIDEN_USERS,
  ...
)
```

But can also be expressed in separate validators, notice that order matters
because validators are evaluated in the given order.

```python
validators = [
  Validator("NAME", ne="john"),
  Validator("NAME", len_min=4),
  Validator("NAME", must_exist=True),
  Validator("NAME", startswith="user_"),
]
```

## Custom validation messages

Messages can be customized by passing a `messages` argument to the `Validator` constructor.

The messages argument must be passed a dictionary with one of the valid keys:

The default messages are:

```python
{
    "must_exist_true": "{name} is required in env {env}",
    "must_exist_false": "{name} cannot exists in env {env}",
    "condition": "{name} invalid for {function}({value}) in env {env}",
    "operations": (
        "{name} must {operation} {op_value} "
        "but it is {value} in env {env}"
    ),
    "combined": "combined validators failed {errors}",
}
```

Example:

```python
Validator(
    "VERSION",
    must_exist=True,
    messages={"must_exist_true": "You forgot to set {name} in your settings."}
)
```

## Lazy validation

Instead of passing `validators=` argument to `Dynaconf` class you can register validators after the instance is created.

```python
settings = Dynaconf(...)

custom_msg = "You cannot set {name} to {value} in env {env}"
settings.validators.register(
    Validator("MYSQL_HOST", eq="development.com", env="DEVELOPMENT"),
    Validator("MYSQL_HOST", ne="development.com", env="PRODUCTION"),
    Validator("VERSION", ne=1, messages={"operations": custom_msg}),
    Validator("BLABLABLA", must_exist=True),
)
```

Having the list of validators registered you can call one of:

### Validate and raise on the first error:

```python
settings.validators.validate()
```

### Validate and accumulate errors, raise only after all validators are evaluated.

```python
settings.validators.validate_all()
```

The raised `ValidationError` will have an attribute `details` holding information about each
error raised.

### Providing default or computed values


Validators can be used to provide default or computed values.

#### Default values

```py
Validator("FOO", default="A default value for foo")
```

Then if not able to load the values from files or environment this default value will be set for that key.


!!! warning
    YAML reads empty keys as `None` and in that case defaults are not applied, if you want to change it
    set `apply_default_on_none=True` either globally to `Dynaconf` class or individually on a `Validator`.

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

### Casting / Transform

Validators can be used to cast values to a specific type,
the `cast` argument expects a class/type or callable.

given this settings.toml 
```toml
name = 'Bruno'
colors = ['red', 'green', 'blue']
``` 

Validators can be passed a `cast` attribute

```python
settings = Dynaconf(
    validators=[
        # Order matters here
        Validator("name", len_eq=5),
        Validator("name", len_min=1),
        Validator("name", len_max=5),
        # This will cast the str to list
        Validator("name", cast=list),
        # From this point on Validation pipeline
        # `name` will be a list of chars
        # and this will affect the settings.NAME

        Validator("colors", len_eq=3),
        Validator("colors", len_eq=3),
        # this will cast the list to str
        Validator("colors", len_eq=24, cast=str),
        # From this point on Validation pipeline
        # `colors` will be a str of 24 chars
        # and this will affect the settings.COLORS

    ],
)
```

```python
assert settings.name == ['B', 'r', 'u', 'n', 'o']
assert type(settings.name ) == list
assert settings.colors == '["red", "green", "blue"]'
assert type(settings.colors) == str
```

### Callable conditions 

The `condition` argument expects a callable that receives the value and returns a 
boolean value. If the condition is not met a `ValidationError` will be raised.

To pass the validation the condition function must return `True` (or a truthy type)
if the returned value is `False` (or a falsy type) then the condition fails.

The condition callable receives only a single value as a parameter.

Example:

```python
Validator("VERSION", condition=lambda v: v.startswith("1."))


def user_must_be_chuck_norris(value):
    return value == "Chuck Norris"

Validator("USER", condition=user_must_be_chuck_norris)
```

### Conditional Validators 

In some cases you might want to perform a validation only when 
another validator passes, for example:

> Ensure that the `DATABASE.HOST` is set only when `DATABASE.USER` is set.

To validate that case the parameter `when` can be passed:

```python
Validator(
    "DATABASE.HOST", 
    must_exist=True, 
    when=Validator("DATABASE.USER", must_exist=True)
)
```

Another example:

> validate `DATABASE.CONNECTION_ARGS` is set only when `DATABASE.URI startswith "sqlite://"`

```python
Validator(
    "DATABASE.CONNECTION_ARGS", 
    must_exist=True, 
    when=Validator("DATABASE.URI", condition=lambda v: v.startswith("sqlite://")),
    messages={"must_exist_true": "{name} is required when DATABASE is SQLite"}
)
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

`dynaconf_validators.toml` is equivalent to the program below:

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

You can specify if you want to validate all environments defined for a validator (default behavior) or only the current environment. In the first case, the validators will run on all possible settings defined in their list of environments, while in the latter the validators with environments different from the current environment will be skipped.

This is useful when your configuration for different environments (let's say `production` and `development`) comes from different files you don't necessarily have access to during development. You would want to write different validators for your `development` and `production` environments, and only run the right validator for the current environment.

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
        # Ensure some parameters exist for both envs
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
