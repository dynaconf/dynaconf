import json
import os

import toml
from box import BoxKeyError

from dynaconf.utils.boxing import DynaBox

true_values = ("t", "true", "enabled", "1", "on", "yes", "True")
false_values = ("f", "false", "disabled", "0", "off", "no", "False", "")


class MetaValue:
    """A Marker to trigger specific actions on `set` and `object_merge`"""

    meta_value = True

    def __init__(self, value):
        self.value = parse_conf_data(value, tomlfy=True)

    def __repr__(self):
        return "{_class}({value}) on {_id}".format(
            _class=self.__class__.__name__, value=self.value, _id=id(self)
        )


class Reset(MetaValue):
    """Triggers an existing key to be reset to its value"""

    dynaconf_reset = True


class Del(MetaValue):
    """Triggers an existing key to be deleted"""

    dynaconf_del = True


class Merge(MetaValue):
    """Triggers an existing key to be merged"""

    dynaconf_merge = True


converters = {
    "@int": int,
    "@float": float,
    "@bool": (
        lambda value: True if str(value).lower() in true_values else False
    ),
    "@json": json.loads,
    # Meta Values to trigger pre assignment actions
    "@reset": lambda value: Reset(value),
    "@del": lambda value: Del(value),
    "@merge": lambda value: Merge(value),
    # Special markers to be used as placeholders e.g: in prefilled forms
    # will always return None when evaluated
    "@note": lambda value: None,
    "@comment": lambda value: None,
    "@null": lambda value: None,
    "@none": lambda value: None,
}


def parse_with_toml(data):
    """Uses TOML syntax to parse data"""
    try:
        return toml.loads("key={}".format(data), DynaBox).key
    except (toml.TomlDecodeError, BoxKeyError):
        return data


def _parse_conf_data(data, tomlfy=False):
    """
    @int @bool @float @json (for lists and dicts)
    strings does not need converters

    export DYNACONF_DEFAULT_THEME='material'
    export DYNACONF_DEBUG='@bool True'
    export DYNACONF_DEBUG_TOOLBAR_ENABLED='@bool False'
    export DYNACONF_PAGINATION_PER_PAGE='@int 20'
    export DYNACONF_MONGODB_SETTINGS='@json {"DB": "quokka_db"}'
    export DYNACONF_ALLOWED_EXTENSIONS='@json ["jpg", "png"]'
    """
    cast_toggler = os.environ.get("AUTO_CAST_FOR_DYNACONF", "true").lower()
    castenabled = cast_toggler not in false_values

    if (
        castenabled
        and data
        and isinstance(data, str)
        and data.startswith(tuple(converters.keys()))
    ):
        parts = data.partition(" ")
        converter_key = parts[0]
        value = parts[-1]
        return converters.get(converter_key)(value)

    return parse_with_toml(data) if tomlfy else data


def parse_conf_data(data, tomlfy=False):
    if isinstance(data, (tuple, list)):
        # recursively parse each sequence item
        return [parse_conf_data(item, tomlfy=tomlfy) for item in data]
    elif isinstance(data, (dict, DynaBox)):
        # recursively parse inner dict items
        _parsed = {}
        for k, v in data.items():
            _parsed[k] = parse_conf_data(v, tomlfy=tomlfy)
        return _parsed
    else:
        # return parsed string value
        return _parse_conf_data(data, tomlfy=tomlfy)


def unparse_conf_data(value):
    if isinstance(value, bool):
        return "@bool %s" % value
    elif isinstance(value, int):
        return "@int %s" % value
    elif isinstance(value, float):
        return "@float %s" % value
    elif isinstance(value, (list, dict)):
        return "@json %s" % json.dumps(value)
    elif value is None:
        return "@none "
    else:
        return value
