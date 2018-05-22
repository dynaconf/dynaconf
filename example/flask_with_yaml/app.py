# coding: utf-8

from flask import Flask, render_template
from dynaconf import FlaskDynaconf


# create your app
app = Flask(__name__)

FlaskDynaconf(
    app,
    ENVVAR_FOR_DYNACONF="MYSITE_SETTINGS_MODULE",
    ENV_FOR_DYNACONF='MYSITE',
    SETTINGS_MODULE_FOR_DYNACONF='settings.yml,.secrets.yml',
    EXTRA_VALUE='You can add aditional config vars here'
)


@app.route('/')
def index():
    return render_template('dynaconf.html')


app.add_url_rule(app.config.TEST_RULE, view_func=lambda: 'test')


if __name__ == '__main__':
    app.run()
