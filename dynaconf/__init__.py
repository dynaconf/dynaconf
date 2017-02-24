# coding: utf-8
from dynaconf.base import LazySettings
from dynaconf.validator import Validator
from dynaconf.transformator import Transformator

settings = LazySettings()

__all__ = ['settings', 'LazySettings', 'Validator', 'Transformator']
