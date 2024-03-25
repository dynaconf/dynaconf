# Validation

## Overview

Dynaconf allows the validation of settings parameters, for cases where you want to validate the settings before starting the program.

## Usage

To define validation rules, you must create `Validator` objects, which are constructed using keys (positional arguments) and rules (kwargs). For example:

```python
Validator("AGE", gte=20, lte=80) # multiple rules
Validator("NAME", "VERSION", "PORT", must_exist=True) # multiple keys
Validator("DB.PORT", eq=8080) # keys with dot-path notation
```

In the first sections, we'll see some different ways to use `Validator` objects.
For an extensive description of available validators, see the [Reference](#reference) section.

### With Python

#### On instantiation

When you instantiate your settings, the declared validators won't be immediately run.
They'll be first triggered upon trying to access some setting, and only the first exception will be raised:


=== "app.py"

    ```python
    from dynaconf import Dynaconf, Validator

    settings = Dynaconf(
        settings_file=["settings.toml"],
        environments=True,
        validators=[
            # Ensure some parameter meets a condition
            Validator("AGE", lte=30, gte=10),
            # Only the first ValidationError will be raised
            Validator("NAME", eq="John"),
        ],
    )

    # The following three lines will trigger a validation error:
    print(settings.age)
    print(settings.validators)
    print(settings.as_dict())
    ```

=== "settings.toml"

    ```toml
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

=== "output"

    ```bash
    $ python app.py
    (...)
    dynaconf.validator.ValidationError: AGE must lte 30 but it is 35 in env DEVELOPMENT
    ```

!!! warning
    Sometimes an external library might implicitly access your settings object through module inspection.
    This may may trigger an undesired validation, even without an explicit access call in your code.

    If you are running into early validation triggering problems, consider if this is not the case.

#### Lazy validation

Instead of passing `validators=` argument to `Dynaconf` class you can register validators
after the instance is created and trigger validation manually.

<h5>Register</h5>

First, register some validators. This won't trigger the validation yet.

```python
settings = Dynaconf()

settings.validators.register(
    Validator("MYSQL_HOST", eq="development.com", env="DEVELOPMENT"),
    Validator("MYSQL_HOST", ne="development.com", env="PRODUCTION"),
)
```

<h5>Trigger manually</h5>

You may choose two strategies for the validation:

- `validate`: raises `ValidationError` on the first error found.
- `validate_all`: raises `ValidationError` at the end. Accumulative error data is stored at `details`.

```python
# raises on first error found
settings.validators.validate()

# raises after all possible errors are evaluated
try:
    settings.validators.validate_all()
except dynaconf.ValidationError as e:
    accumulative_errors = e.details
    print(accumulative_errors)
```

<h5>Trigger on data update</h5>

By default, if the data of an instance is updated with `update`, `set` or `load_file` methods,
no validation will be triggered.

You can override this globally with the option [validate_on_update](configuration.md/#validate_on_update) or
set this on a per-call basis.

```python
# validate_on_update=False (default)
settings.update({"NEW_VALUE": 123}, validate=True) # triggers validators.validate()
settings.update({"NEW_VALUE": 123}, validate="all") # triggers validators.validate_all()

# validate_on_update=True or "all"
settings.update({"NEW_VALUE": 123}) # will trigger with the global strategy
```

### With CLI

It is possible to define validators in a `TOML` file called `dynaconf_validators.toml` placed in the same folder as your settings files. For more information, see the [CLI section](cli.md#dynaconf-validate).

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

## Features

### Multiple Validators

A single validator can have multiple conditions.

```python
Validator(
  "NAME",
  ne="john",
  len_min=4,
  must_exist=True, # redundant but allowed
  startswith="user_",
  cast=str,
  condition=lambda v: v not in FORBIDDEN_USERS,
  ...
)
```

But it can also be expressed in separate validators. Notice that order matters because validators are evaluated in the given order.

```python
validators = [
  Validator("NAME", ne="john"),
  Validator("NAME", len_min=4),
  Validator("NAME", must_exist=True),
  Validator("NAME", startswith="user_"),
]
```

### Custom messages

Messages can be customized by passing a `messages` argument to the `Validator` constructor. This argument must be passed a `dict` with one of the valid keys, shown in the `dict` below which contains the default messages:

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

Note that these default messages also show all the variables that can be interpolated to each message.

<h4>Example</h4>

```python
Validator(
    "VERSION",
    must_exist=True,
    messages={"must_exist_true": "You forgot to set {name} in your settings."}
)
```

### Default values

Validators can be used to provide default values, which can be either static or computed.

<h4> Static default values </h4>

If `Dynaconf` fails to load a value for the given setting, it'll give it the exact value provided in `default`.

```py
Validator("FOO", default="A default value for foo")
```

!!! warning
    YAML reads empty keys as `None` and in that case defaults are not applied, if you want to change it
    set `apply_default_on_none=True` either globally to `Dynaconf` class or individually on a `Validator`.

<h4> Computed default values </h4>

Sometimes you need some values to be computed by calling functions.

<h5>Eager evaluation</h5>
If you want the function to be run during validation time, define it with this signature:

```py

def my_function(settings, validator):
    return "this is computed during validation time"

```

and pass it directly to the `default` kwarg:

```py
Validator("FOO", default=my_function)
```

<h5>Lazy evaluation</h5>
If you want the default to be evaluated when the value is first accessed, define `my_function` with this signature:

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

and pass it to the `default` kwarg like so:

```py
from dynaconf.utils.functional import empty
from dynaconf.utils.parse_conf import Lazy

Validator("FOO", default=Lazy(empty, formatter=my_lazy_function))

```

### Casting / Transform

Validators can be used to postprocess your settings after being loaded from the files by passing a `Callable` to the `cast` argument. For example, they can be used to cast their type.

This `Callable` will get called with the setting's value as its single argument (note that this could potentially be a `list` or `dict` depending on your setting path) and its return value will be assigned to the provided setting path.

Note that you can pass any `Callable` such as regular function or a class/type.

<h4>Example</h4>

Given this `settings.toml`

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

assert settings.name == ['B', 'r', 'u', 'n', 'o']
assert type(settings.name ) == list
assert settings.colors == '["red", "green", "blue"]'
assert type(settings.colors) == str
```

!!! info
    When multiple validators for the same field specifies a `cast`, Dynaconf will execute both in order, so the end result in the settings object is the result of the cumulative pipeline.

### Custom conditional expressions

The `condition` argument expects a `Callable` that receives the setting's value as its only argument and returns a `bool`.

To pass the validation, the condition function must return `True` (or a truthy type, such that `bool(x) == True`). If the returned value is `False` (or a falsy type, such that `bool(x) == False`) then the condition fails, and a `ValidationError` is risen.

<h4>Example</h4>

```python
Validator("VERSION", condition=lambda v: v.startswith("1."))


def user_must_be_chuck_norris(value):
    return value == "Chuck Norris"

Validator("USER", condition=user_must_be_chuck_norris)
```

### Conditional Validation

In some cases you might want to perform a validation only when another validator passes. To do this, use the `when` parameter.

<h4>Simple Example</h4>

Say you want to ensure that the `DATABASE.HOST` is set only when `DATABASE.USER` is set. To do so, pass another `Validator` to `when`:

```python
Validator(
    "DATABASE.HOST",
    must_exist=True,
    when=Validator("DATABASE.USER", must_exist=True)
)
```

<h4>Complex Example</h4>

Say you want to validate that `DATABASE.CONNECTION_ARGS` is set only when `DATABASE.URI` starts with `"sqlite://"`. This will do that for you:

```python
Validator(
    "DATABASE.CONNECTION_ARGS",
    must_exist=True,
    when=Validator("DATABASE.URI", condition=lambda v: v.startswith("sqlite://")),
    messages={"must_exist_true": "{name} is required when DATABASE is SQLite"}
)
```

### Combination Operators

Validators can be combined using `|` or `&`.

<h4> <b>or</b> operator (<code>|</code>) </h4>

```py
Validator('DATABASE.USER', must_exist=True) | Validator('DATABASE.KEY', must_exist=True)
```

which generates a single `Validator` which succeeds if any of these pass.

<h4> <b>and</b> operator (<code>&</code>) </h4>

```py
Validator('DATABASE.HOST', must_exist=True) & Validator('DATABASE.CONN', must_exist=True)
```

which generates a single `Validator` which succeeds only if both of these pass.

### Selective Validation

> **New in 3.1.6**

You can also choose what sections of the settings you do or don't want to validate. This is achieved by using the `validate_only` and `validate_exclude` kwargs to `Dynaconf` (read more in the [Configuration](configuration.md) page) or by passing `only` or `exclude` to the `validate` method of the `Dynaconf.validators` list.

This is useful when:

- You want to add additional validators after the settings object is created.
- You want settings validated only when certain sections of your project are loaded.
- You want to offer incremental configuration levels, validating only what is needed.

Note that _exclusions are applied after selections_. Therefore, if you pass a settings path in `only` that also matches a path passed in `exclude`, it'll end up excluded.

A settings path starts at the top level element and can be specified down to the lowest component. For example: `my_settings.server.user.password` can have the following settings paths passed in `server`, `server.user`, `server.user.password`.

*Note:* Selective validation matches the passed in value(s) to settings paths that **start with that value**. This means that passing `exclude="FOO"` will exclude not only paths that start with `FOO` but also `FOOBAR`.

<h4>Example</h4>

In this example, the behavior is as follows:

1. Dynaconf will _only_ validate any setting that starts with `server` upon instantiation.
2. Only settings that start with `module1` will be validated when `module1.py` is first run.
3. When `module2.py` is first run, only settings that start with `module2` (excluding those that start with `module2.bad`) will be validated.

`config.py`

```python
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

`module1.py`

```python
# call validation on module1 settings
settings.validators.validate(only=["module1"])
```

`module2.py`

```python
# call validation on module2 settings
# ignore validation for a subsection of module2's settings
settings.validators.validate(
    only=["module2"],
    exclude=["module2.bad"]
)
```

### Validating only the `current_env`

You can specify if you want to validate all environments defined for a validator (default behavior) or only the current environment. To do so, you may use the `only_current_env` argument of single `Validator`s (i.e., in `Validator.validate`), the same argument on `ValidatorList`s (such as `Dynaconf.validators.validate`) or by passing the `validate_only_current_env` kwarg to `Dynaconf` (see [Configuration](configuration.md)).

In the first case, the validators will run on all possible settings defined in their list of environments, while in the latter the validators with environments different from the current environment will be skipped.

This is useful when your configuration for different environments (let's say `production` and `development`) comes from different files you don't necessarily have access to during development. You would want to write different validators for your `development` and `production` environments, and only run the right validator for the current environment.

It's also useful if certain settings are only required in `production`.

<h4>Example</h4>

Using:

`settings.toml`

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

`.secrets.toml`

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
        Validator('VERSION', 'NAME', 'SERVERS', env=['development', 'production'], must_exist=True),

        # Ensure some parameter validate certain condition in dev env
        Validator("SERVERS", env='development', cont='localhost'),

        # Ensure some parameter exists in production env
        Validator('API_KEY', env='production', must_exist=True),
    ]
)
```

And suppose during development, when `settings.current_env == 'development'`, you don't have the file `.secrets.toml`.

Running `settings.validators.validate()` will fail even if `settings.current_env == 'development'`, because by default all validators will run on all of their environments, whether or not it is the current env.

If you instantiate your settings with the parameter `validate_only_current_env=True`, no errors will be raised if `settings.current_env == 'development'`, but a `ValidationError` will raise if `settings.current_env == 'production'`. This forces you to have the `.secrets.toml` file in `production` but not during `development`.

## Reference

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
# Conditionally runs the validator only when the passed validator passes
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
