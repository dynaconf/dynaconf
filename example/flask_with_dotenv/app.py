# coding: utf-8

from flask import Flask, render_template
from dynaconf.contrib import FlaskDynaconf

# create your app
app = Flask(__name__)

# will populate app.config from .env + environment variables
FlaskDynaconf(app)


@app.route('/')
def index():
    return render_template('dynaconf.html')


@app.route('/test')
def test():
    return app.config['HELLO']


app.add_url_rule(app.config.TEST_RULE, view_func=lambda: 'test')
