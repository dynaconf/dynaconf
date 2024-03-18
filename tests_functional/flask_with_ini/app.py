from __future__ import annotations

from flask import Flask
from flask import render_template

from dynaconf import FlaskDynaconf

# create your app
app = Flask(__name__)

FlaskDynaconf(app)


@app.route("/")
def index():
    return render_template("dynaconf.html")


app.add_url_rule(app.config.TEST_RULE, view_func=lambda: "test")


if __name__ == "__main__":
    app.run()
