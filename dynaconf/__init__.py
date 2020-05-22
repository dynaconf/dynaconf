import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

from dynaconf.base import LazySettings  # noqa
from dynaconf.contrib import DjangoDynaconf  # noqav
from dynaconf.contrib import FlaskDynaconf  # noqa
from dynaconf.validator import ValidationError  # noqa
from dynaconf.validator import Validator  # noqa

settings = LazySettings()
Dynaconf = LazySettings  # noqa

__all__ = [
    "settings",
    "Dynaconf",
    "LazySettings",
    "Validator",
    "FlaskDynaconf",
    "ValidationError",
    "DjangoDynaconf",
]
