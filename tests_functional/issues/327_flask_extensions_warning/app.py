from __future__ import annotations

from dynaconf import FlaskDynaconf
from flask import Flask

app = Flask(__name__)

FlaskDynaconf(app, extensions_list=True)
