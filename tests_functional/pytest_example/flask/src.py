from __future__ import annotations

from flask import Flask

from dynaconf.contrib import FlaskDynaconf


def create_app(**config):
    app = Flask(__name__)
    FlaskDynaconf(app, **config)
    return app
