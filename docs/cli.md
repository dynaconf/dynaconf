

## settings instance

Every command (except the init) will require the Instance can be set using `-i` parameter or `export INSTANCE_FOR_DYNACONF`


## The dynaconf CLI

The `$ dynaconf -i config.settings` cli provides some useful commands

> **IMPORTANT** if you are using [Flask Extension](/flask/) the env var `FLASK_APP` must be defined to use the CLI, and if using [Django Extension](/django/) the `DJANGO_SETTINGS_MODULE` must be defined.

### dynaconf --help

```
Usage: dynaconf [OPTIONS] COMMAND [ARGS]...

  Dynaconf - Command Line Interface

Options:
  --version  Show dynaconf version
  --docs     Open documentation in browser
  --banner   Show awesome banner
  -i, --instance TEXT  Custom instance of LazySettings
  --help     Show this message and exit.

Commands:
  init      Inits a dynaconf project By default it...
  list      Lists all defined config values
  write     Writes data to specific source
  validate  Validates based on dynaconf_validators.toml file
```

### dynaconf init

Use init to easily configure your application configuration, once dynaconf is installed go to the root directory of your application and run:

creates settings files in current directory

```
$ dynaconf -i init -v key=value -v foo=bar -s token=1234 -e production
```

The above command will create in the current directory

`settings.toml`

```ini
[default]
KEY = "default"
FOO = "default"

[production]
KEY = "value"
FOO = "bar"
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

> For sensitive data in production is recommended using [Vault Server](/secrets/)

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
  --django TEXT
  --help                          Show this message and exit.

```

### dynaconf list

List all defined parameters and optionally export to a json file.

```
Usage: dynaconf list [OPTIONS]

  Lists all user defined config values and if `--all` is passed it also
  shows dynaconf internal variables.

Options:
  -e, --env TEXT     Filters the env to get the values
  -k, --key TEXT     Filters a single key
  -m, --more         Pagination more|less style
  -l, --loader TEXT  a loader identifier to filter e.g: toml|yaml
  -a, --all          show dynaconf internal settings?
  -o, --output FILE  Filepath to write the listed values as json
  --output-flat      Output file is flat (do not include [env] name)
  --help             Show this message and exit.
```

#### Exporting current environment as a file

```bash
dynaconf list -o path/to/file.yaml
```

The above command will export all the items showed by `dynaconf list` to the desired format which is inferred by the `-o` file extension, supported formats `yaml, toml, ini, json, py`

When using `py` you may want a flat output (without being nested inside the env key)

```bash
dynaconf list -o path/to/file.py --output-flat
```

### dynaconf write

```
Usage: dynaconf write [OPTIONS] TO

  Writes data to specific source

Options:
  -v, --vars TEXT     key values to be written e.g: `dynaconf write toml
                      -e NAME=foo -e X=2
  -s, --secrets TEXT  secret key values to be written in .secrets e.g:
                      `dynaconf write toml -s TOKEN=kdslmflds -s X=2
  -p, --path TEXT     defaults to current directory/settings.{ext}
  -e, --env TEXT      env to write to defaults to DEVELOPMENT for files for
                      external sources like Redis and Vault it will be
                      DYNACONF or the value set in $ENVVAR_PREFIX_FOR_DYNACONF
  -y
  --help              Show this message and exit.
```

### dynaconf validate

> **NEW in 1.0.1**

Starting on version 1.0.1 it is possible to define validators in **TOML** file called **dynaconf_validators.toml** placed in the same folder as your settings files.

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
$ dynaconf -i config.settings validate
```

If validates it returns status 0 (success) and this command can be called in your CI/CD/Deploy jobs.

### dynaconf --version

returns dynaconf version

```
$ dynaconf -i config.settings --version
1.0.0
```

### dynaconf --docs

Opens Dynaconf documentation in browser


### dynaconf --banner

Prints this awesome ascii made banner in the console :)

```
$ dynaconf -i config.settings --banner

██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝

Learn more at: http://github.com/rochacbruno/dynaconf
```
