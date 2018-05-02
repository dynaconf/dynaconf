# coding: utf-8

from flask import Flask, render_template
from dynaconf.contrib import FlaskDynaconf


# create your app
app = Flask(__name__)

"""
# Before doing anything with app apply FlaskDynaconf

The arguments are.
app = The created app
dynaconf_args = Extra args to be passed to Dynaconf (validator for example)

All other values are stored as config vars specially:

ENVVAR_FOR_DYNACONF = Name of environment variable to use if you want to
                      change the settings file from env vars
                      example:
                         export MYSITE_SETTINGS_MODULE=/tmp/settings.py
                      with the above the settings will be loaded from that file
                      Dynaconf supports .py, .yml, .toml

DYNACONF_NAMESPACE = Namespace prefix for your envvars to become settings
                     example:
                         export MYSITE_SQL_PORT='@int 5445'

                     with that exported to env you access using:
                         app.config.SQL_PORT
                         app.config.get('SQL_PORT')
                         app.config.get('sql_port')  # get is case insensitive
                         app.config['SQL_PORT']

                    Dynaconf uses `@int, @bool, @float, @json` to cast env vars

SETTINGS_MODULE_FOR_DYNACONF = The name of the module or file to use as
                               default to load settings. If nothing is passed
                               it will be `settings.py` or value found in
                               `ENVVAR_FOR_DYNACONF`
                               Dynaconf supports .py, .yml, .toml

YAML = If using YAML for settings module, you pass an extra yaml file here
       It is general useful to have a different file to store secrets
       example `.secrets.yml` and then values in that file will
       override other values. And you can exclude the .secrets from your
       public repositories.

------------------------------------------------------------------------------

ATTENTION: Take a look at `settings.yml` and `.secrets.yml` to know the
           required settings format.

Settings load order in Dynaconf:
0) Load all defaults and Flask defaults
1) Load all passed variables when applying FlaskDynaconf
2) Update with data in SETTINGS_MODULE_FOR_DYNACONF
3) Update with data in YAML extra file if provided
4) Update with data in environmente vars `DYNACONF_NAMESPACE_`

YAML files are very useful to have `namespaced` settings, lets say,
`production` and `development`.

You can also achieve the same using multiple `.py` files naming as
`settings.py`, `production_settings.py` and `development_settings.py`
(see examples/validator)

Now lets apply FlaskDynaconf to this app.

"""

FlaskDynaconf(
    app,
    ENVVAR_FOR_DYNACONF="MYSITE_SETTINGS_MODULE",
    DYNACONF_NAMESPACE='MYSITE',
    SETTINGS_MODULE_FOR_DYNACONF='settings.yml',
    YAML='.secrets.yml',
    EXTRA_VALUE='You can add aditional config vars here'
)


@app.route('/')
def index():
    return render_template('dynaconf.html')


if __name__ == '__main__':
    app.run()
