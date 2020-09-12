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

If you want to be lazy evaluated

```py

from dynaconf.utils.parse_conf import empty, Lazy

Validator("FOO", default=Lazy(empty, formatter=my_function))

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

> **NEW in 1.0.1**

Starting on version 1.0.1 it is possible to define validators in **TOML** file called **dynaconf_validators.toml** placed in the same folder as your settings files.

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
