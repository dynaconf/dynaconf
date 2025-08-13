"""Dynaconf configuration for generate docs test."""

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.py"]
)