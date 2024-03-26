from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import Validator

settings = Dynaconf(var="dynaconf")


def a(v):
    print("called a, replace conf -> settings")
    return v.replace("conf", "settings")


def b(v):
    print("called b, transform to upper DYNASETTINGS")
    return v.upper()


validators = [
    Validator("var", cast=a),
    Validator("var", cast=b),
]

settings.validators.register(*validators)
settings.validators.validate_all()


assert settings.var == "DYNASETTINGS", settings.var
