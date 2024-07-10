# So you have a function that retrieves data from external source

CACHE = {}  # could be Redis


def get_data_from_somewhere(settings, result, key, *args, **kwargs):
    """Your function that goes to external service like gcp, aws, vault, etc"""
    # result.value is 'special:/foo/bar:token'
    if key in CACHE:
        return CACHE[key]

    if isinstance(result.value, str) and result.value.startswith("@special:"):
        _, path, key = result.value.split(":")
        # value = get_value_from_special_place(path, key)
        value = CACHE[key] = "lets believe it was retrieved from special place"
        return value

    return result


# ---

from dynaconf import Dynaconf
from dynaconf.hooking import Action
from dynaconf.hooking import Hook
from dynaconf.hooking import HookableSettings

# Create a Dynaconf instance
settings = Dynaconf(
    # set the Hookable wrapper class
    _wrapper_class=HookableSettings,
    # Register your hooks, you can have AFTER_GET, BEFORE_GET
    # you can have multiple hooks, value passes from one to another
    _registered_hooks={Action.AFTER_GET: [Hook(get_data_from_somewhere)]},
)

# this value can actually come from settings files or envvars
settings.set("token", "@special:/vault/path:token")

assert settings.token == "lets believe it was retrieved from special place"

# from cache this time
assert settings.token == "lets believe it was retrieved from special place"
