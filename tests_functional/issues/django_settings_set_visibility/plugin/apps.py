from __future__ import annotations

from django.apps import AppConfig


class PluginConfig(AppConfig):
    name = "plugin"
    default_auto_field = "django.db.models.BigAutoField"
