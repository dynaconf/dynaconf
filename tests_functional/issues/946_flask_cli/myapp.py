"""
CLI wouldnt recognize FLASK_APP "entrypoint" path (foo.bar:app)

https://github.com/dynaconf/dynaconf/issues/946
"""

from __future__ import annotations

from dynaconf import FlaskDynaconf
from flask import Flask

app = Flask(__name__)
FlaskDynaconf(app)
