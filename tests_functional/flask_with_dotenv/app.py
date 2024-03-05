from __future__ import annotations

from dynaconf.contrib import FlaskDynaconf
from flask import Flask
from flask import render_template

# create your app
app = Flask(__name__)

# will populate app.config from .env + environment variables
FlaskDynaconf(app)


@app.route("/")
def index():
    return render_template("dynaconf.html")


@app.route("/test")
def test():
    return app.config["HELLO"]


app.add_url_rule(
    app.config.get("TEST_RULE", "/default_route"), view_func=lambda: "test"
)


if __name__ == "__main__":
    app.run()
