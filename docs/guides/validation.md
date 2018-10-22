# Validation

Dynaconf allows the validation of settings parameters, in some cases you may want to validate the settings before starting the program.

Lets say you have `settings.toml`

```ini
[default]
version = "1.0.0"
age = 35
name = "Bruno"

[production]
PROJECT = "This is not hello_world"
```

## Validating in Python programatically

At any point of your program you can do:

```python
from dynaconf import settings, Validator

# Register validators
settings.validators.register(
    # Ensure some parameters exists (are required)
    Validator('VERSION', 'AGE', 'NAME', must_exist=True),

    # Ensure some password cannot exist
    Validator('PASSWORD', must_exist=False),

    # Ensure some parameter mets a condition
    # conditions: (eq, ne, lt, gt, lte, gte, identity, is_type_of, is_in, is_not_in)
    Validator('AGE', lte=30, gte=10),

    # validate a value is eq in specific env
    Validator('PROJECT', eq='hello_world', env='production'),
)

# Fire the validator
settings.validators.validate()
```

The above will raise `dynaconf.validators.ValidationError("AGE must be lte=30 but it is 35 in env DEVELOPMENT")` and `dynaconf.validators.ValidationError("PROJECT must be eq='hello_world' but it is 'This is not hello_world' in env PRODUCTION")`

You can also use dot-delimited paths for registering validators on nested structures:

```python
from dynaconf import settings, Validator

# Register validators
settings.validators.register(

    # Ensure the database.host field exists.
    Validator('DATABASE.HOST', must_exist=True),

    # Make the database.password field optional.
    Validator('DATABASE.PASSWORD', must_exist=True),

# Fire the validator
settings.validators.validate()
```

## CLI and dynaconf_validators.toml

> **NEW in 1.0.1**

Starting on version 1.0.1 it is possible to define validators in **TOML** file called **dynaconf_validators.toml** placed in the same fodler as your settings files.

`dynaconf_validators.toml` equivalent to program above

```ini
[default]

version = {must_exist=true}
name = {must_exist=true}
password = {must_exist=false}

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
