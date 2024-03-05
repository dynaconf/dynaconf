from __future__ import annotations

from dynaconf.contrib import FlaskDynaconf
from flask import Flask


def create_app(**config):
    app = Flask(__name__)
    FlaskDynaconf(app, **config)
    return app
