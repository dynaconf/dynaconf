# Flask Extension

Dynaconf provides a drop in replacement for `app.config`.

As Flask encourages the composition by overriding the `config_class` attribute this extension follows the [patterns of Flask](http://flask.pocoo.org/docs/0.12/patterns/subclassing/) and turns your Flask's `app.config` in to a `dynaconf` instance.

## Initialize the extension

Initialize the **FlaskDynaconf** extension in your `app`

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app)
```

> You can optionally use `init_app` as well.

## Use `FLASK_` environment variables

Then the `app.config` will work as a `dynaconf.settings` instance and `FLASK_` will be the global prefix for exporting environment variables.

Example:

```bash
export FLASK_DEBUG=true              # app.config.DEBUG
export FLASK_INTVALUE=1              # app.config['INTVALUE']
export FLASK_MAIL_SERVER='host.com'  # app.config.get('MAIL_SERVER')
```

## Settings files

You can also have settings files for your Flask app, in the root directory (the same where you execute `flask run`) put your `settings.toml` and `.secrets.toml` files and then define your environments `[default]`, `[development]` and `[production]`.

To switch the working environment the `FLASK_ENV` variable can be used, so `FLASK_ENV=development` to work
in development mode or `FLASK_ENV=production` to switch to production.

> **IMPORTANT**: To use `$ dynaconf` CLI the `FLASK_APP` must be defined.

IF you don't want to manually create your config files take a look at the [CLI](cli.html)

## Customizations

It is possible to customize how your Flask project will load settings, example: You want your users to customize a settings file defined in `export PROJECTNAME_SETTINGS=/path/to/settings.toml` and you want environment variables to be loaded from `PROJECTNAME_VARNAME`

your flask `app.py` (or wherever you setup dynaconf)

```python
GLOBAL_ENV_FOR_DYNACONF = "PROJECTNAME"
"""This defines which environment variable global prefix dynaconf will load
That means that `export PROJECTNAME_FOO=1` will be loaded to `app.config.FOO
On command line it is possible to check it with `dynaconf list -k foo`"""

ENVVAR_FOR_DYNACONF = "PROJECTNAME_SETTINGS"
"""This defines which path dynaconf will look to load config files
example: export PROJECTNAME_SETTINGS=/path/to/settings.toml and the format can be
.ini, .json, .yaml or .toml

e.g::

    export PROJECTNAME_SETTINGS=settings.toml
    [default]
    FOO = 1
    [development]
    FOO = 2
    [production]
    FOO = 3


OR::

    export PROJECTNAME_SETTINGS=settings.yaml
    default:
      foo: 1
    development:
      foo: 2
    production:
      foo: 3


It is also possible to pass a list of files::

    export PROJECTNAME_SETTINGS=settings.toml,other_settings.yaml,another.json

The variables will be cascaded in the defined order (last wins the precedence)
The environment variables wins precedence over all!
"""

# load dynaconf
app = Flask(__name__)
FlaskDynaconf(
    app,
    GLOBAL_ENV_FOR_DYNACONF=GLOBAL_ENV_FOR_DYNACONF,
    ENVVAR_FOR_DYNACONF=ENVVAR_FOR_DYNACONF
)
```

Then the working environment can now be switched using `export PROJECTNAME_ENV=production`
