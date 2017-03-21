# coding: utf-8

from flask import Flask
from dynaconf.contrib import FlaskDynaconf


def test_flask_dynaconf(settings):
    """
    Test Flask app wrapped with FlaskDynaconf
    """
    app = Flask(__name__)
    app.config['MY_VAR'] = 'foo'
    FlaskDynaconf(
        app,
        dynaconf_instance=settings
    )
    assert app.config.HOSTNAME == 'host.com'
    assert app.config.MY_VAR == 'foo'

    assert app.config['HOSTNAME'] == 'host.com'
    assert app.config['MY_VAR'] == 'foo'

    assert app.config.get('HOSTNAME') == 'host.com'
    assert app.config.get('MY_VAR') == 'foo'

    assert app.config('HOSTNAME') == 'host.com'
    assert app.config('MY_VAR') == 'foo'
