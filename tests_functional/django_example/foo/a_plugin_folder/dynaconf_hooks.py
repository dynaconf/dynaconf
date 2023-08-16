from __future__ import annotations

from dynaconf.hooking import Action
from dynaconf.hooking import Hook


def hook_best_boss(temp_settings, value, key, *args, **kwargs):
    """The key BEST_BOSS is not defined anywhere
    but will return what this function returns"""
    if key == "BEST_BOSS":
        return "Michael Scott"
    return value


def post(settings):
    data = {"dynaconf_merge": True}
    if settings.get("ADD_BEATLES") is True:
        data["BANDS"] = ["Beatles"]

    data["_registered_hooks"] = {Action.AFTER_GET: [Hook(hook_best_boss)]}
    return data
