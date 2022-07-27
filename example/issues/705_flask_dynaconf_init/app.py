from __future__ import annotations

from flask import Blueprint
from flask import Flask

blueprint = Blueprint("default", __name__)


@blueprint.route("/")
def index():
    return "Default route."


def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    app.config["ENV"] = "development"
    return app
