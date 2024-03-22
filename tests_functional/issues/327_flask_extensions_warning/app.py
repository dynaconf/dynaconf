from __future__ import annotations

from flask import Flask

from dynaconf import FlaskDynaconf

app = Flask(__name__)

FlaskDynaconf(app, extensions_list=True)
