from flask import Flask

from dynaconf import Dynaconf

settings = Dynaconf(**options)
from dynaconf import FlaskDynaconf


app = Flask(__name__)

settings["MESSAGE"] = "hello"
assert settings["MESSAGE"] == "hello"

FlaskDynaconf(app, dynaconf_instance=settings)

assert app.config["MESSAGE"] == "hello"

app.config.set("MESSAGE", "bye")

assert app.config["MESSAGE"] == "bye", app.config["MESSAGE"]


app.config["MESSAGE"] = "bazinga"

assert app.config["MESSAGE"] == "bazinga"
