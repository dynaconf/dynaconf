import os
import json

from six import string_types
from dynaconf.utils.boxing import DynaBox

true_values = ('t', 'true', 'enabled', '1', 'on', 'yes')
false_values = ('f', 'false', 'disabled', '0', 'off', 'no')

converters = {
    '@int': int,
    '@float': float,
    '@bool': (
        lambda value: True if str(value).lower() in true_values else False
    ),
    '@json': json.loads,
    # Special markers to be used as placeholders e.g: in prefilled forms
    # will always return None when evaluated
    '@note': lambda value: None,
    '@comment': lambda value: None,
    '@null': lambda value: None,
    '@none': lambda value: None,
}


def _parse_conf_data(data):
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
    cast_toggler = os.environ.get('AUTO_CAST_FOR_DYNACONF', '').lower()
    if cast_toggler in false_values:
        return data

    if data and isinstance(
            data, string_types
    ) and data.startswith(tuple(converters.keys())):
        parts = data.partition(' ')
        converter_key = parts[0]
        value = parts[-1]
        return converters.get(converter_key)(value)
    return data


def parse_conf_data(data):
    if isinstance(data, (tuple, list)):
        # recursively parse each sequence item
        return [parse_conf_data(item) for item in data]
    elif isinstance(data, (dict, DynaBox)):
        # recursively parse inner dict items
        _parsed = {}
        for k, v in data.items():
            _parsed[k] = parse_conf_data(v)
        return _parsed
    else:
        # return parsed string value
        return _parse_conf_data(data)


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
