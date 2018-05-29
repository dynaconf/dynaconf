# The dynaconf CLI

The `$ dynaconf` cli provides some useful commands

```
Usage: dynaconf [OPTIONS] COMMAND [ARGS]...

  Dynaconf - Command Line Interface

Options:
  --version  Show dynaconf version
  --docs     Open documentation in browser
  --help     Show this message and exit.

Commands:
  banner    Shows dynaconf awesome banner
  init      Inits a dynaconf project By default it...
  list      Lists all defined config values
  write     Writes data to specific source
  validate  Validates based on dynaconf_validators.toml file
```

## dynaconf init

Use init to easily configure your application configuration, once dynaconf is installed go to the root directory of your application and run:

```
# creates settings files in current directory
$ dynaconf init -v key=value -v otherkey=othervalue -s token=1234 -e production
```

The above command will create in the current directory

`settings.toml`

```ini
[default]
KEY = "default"
OTHERKEY = "default"

[production]
KEY = "value"
OTHERKEY = "othervalue"
```

also `.secrets.toml`

```ini
[default]
TOKEN = "default"

[production]
TOKEN = "1234"
```

The command will also create a `.env` setting the working environment to **[production]**

```bash
ENV_FOR_DYNACONF="PRODUCTION"
```

And will include the `.secrets.toml` in the `.gitignore`

```ini
# Ignore dynaconf secret files
.secrets.*
```

> For sensitive data in production is recommended using [vault server](sensitive_secrets.html)

```
Usage: dynaconf init [OPTIONS]

  Inits a dynaconf project By default it creates a settings.toml and a
  .secrets.toml for [default|development|staging|testing|production|global]
  envs.

  The format of the files can be changed passing --format=yaml|json|ini|py.

  This command must run on the project's root folder or you must pass
  --path=/myproject/root/folder.

  If you want to have a .env created with the ENV defined there e.g:
  `ENV_FOR_DYNACONF=production` just pass --env=production and then .env
  will also be created and the env defined to production.

Options:
  -f, --format [ini|toml|yaml|json|py|env]
  -p, --path TEXT                 defaults to current directory
  -e, --env TEXT                  Sets the working env in `.env` file
  -v, --vars TEXT                 extra values to write to settings file file
                                  e.g: `dynaconf init -v NAME=foo -v X=2
  -s, --secrets TEXT              secret key values to be written in .secrets
                                  e.g: `dynaconf init -s TOKEN=kdslmflds
  --wg / --no-wg
  -y
  --help                          Show this message and exit.
```

## dynaconf list

List all defined parameters

```
Usage: dynaconf list [OPTIONS]

  Lists all defined config values

Options:
  -e, --env TEXT     Filters the env to get the values
  -k, --key TEXT     Filters a single key
  -m, --more         Pagination more|less style
  -l, --loader TEXT  a loader identifier to filter e.g: toml|yaml
  --help             Show this message and exit.
```

## dynaconf write

```
Usage: dynaconf write [OPTIONS] TO

  Writes data to specific source

Options:
  -v, --vars TEXT     key values to be written e.g: `dynaconf write --to toml
                      -e NAME=foo -e X=2
  -s, --secrets TEXT  secret key values to be written in .secrets e.g:
                      `dynaconf write --to toml -s TOKEN=kdslmflds -s X=2
  -p, --path TEXT     defaults to current directory/settings.{ext}
  -e, --env TEXT      env to write to defaults to DEVELOPMENT for files for
                      external sources like Redis and Vault it will be
                      DYNACONF or the value set in $GLOBAL_ENV_FOR_DYNACONF
  -y
  --help              Show this message and exit.
```

## dynaconf validate

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

```
$ dynaconf validate
```

## dynaconf --version

returns dynaconf version

```
$ dynaconf --version
1.0.0
```
