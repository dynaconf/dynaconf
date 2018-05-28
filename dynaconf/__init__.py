# coding: utf-8
from dynaconf.base import LazySettings
from dynaconf.validator import Validator, ValidationError
from dynaconf.contrib import FlaskDynaconf

settings = LazySettings()

__all__ = [
    'settings', 'LazySettings', 'Validator',
    'FlaskDynaconf', 'ValidationError'
]
