import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

from dynaconf.base import LazySettings  # noqa
from dynaconf.contrib import DjangoDynaconf  # noqav
from dynaconf.contrib import FlaskDynaconf  # noqa
from dynaconf.validator import ValidationError  # noqa
from dynaconf.validator import Validator  # noqa

"""This global settings is deprecated from 3.0.0+"""
settings = LazySettings(
    warn_dynaconf_global_settings=True,
    environments=True,
    lowercase_read=False,
    load_dotenv=True,
)

"""This is the new recommended base class alias"""
Dynaconf = LazySettings  # noqa

__all__ = [
    "Dynaconf",
    "LazySettings",
    "Validator",
    "FlaskDynaconf",
    "ValidationError",
    "DjangoDynaconf",
]
