import os
import json
import toml

from six import string_types
from dynaconf.utils import object_merge
from dynaconf.utils.boxing import DynaBox


true_values = (
    't', 'true', 'enabled', '1', 'on', 'yes', 'True'
)
false_values = (
    'f', 'false', 'disabled', '0', 'off', 'no', 'False', ''
)

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


def parse_with_toml(data):
    """Uses TOML syntax to parse data"""
    try:
        return toml.loads('key={}'.format(data), DynaBox).key
    except toml.TomlDecodeError:
        return data


def _parse_conf_data(data, tomlfy=False, obj=None, key=None):
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
    cast_toggler = os.environ.get('AUTO_CAST_FOR_DYNACONF', 'true').lower()
    castenabled = cast_toggler not in false_values

    if castenabled and data and isinstance(data, string_types):
        if data.startswith(tuple(converters.keys())):
            parts = data.partition(' ')
            converter_key = parts[0]
            value = parts[-1]
            return converters.get(converter_key)(value)
        if data.startswith('@merge_unique'):
            return parse_and_merge(
                value=data.partition(' ')[-1],
                key=key,
                obj=obj,
                unique=True
            )
        if data.startswith('@merge'):
            return parse_and_merge(
                value=data.partition(' ')[-1], key=key, obj=obj
            )

    return parse_with_toml(data) if tomlfy else data


def parse_conf_data(data, tomlfy=False, obj=None, key=None):
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
        return _parse_conf_data(data, tomlfy=tomlfy, obj=obj, key=key)


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


def parse_and_merge(value, key, obj, unique=False):
    """
    If data is prefixed with `@merge` try to find existing on obj and merge it
    """
    new = parse_with_toml(value)
    if obj is not None:
        old = obj.get(key)
        _types = (list, tuple, dict)
        if isinstance(new, _types) and isinstance(old, _types):
            object_merge(old, new, unique=unique)
        else:
            raise RuntimeError(
                '@merge casts allows only dict and lists '
                'but it was set to `%s` '
                'toml format for dicts are like: '
                '`@merge {key="value", other="value"}` '
                'and lists are `@merge [1, 2, 3, ...]`'
                % new
            )
    return new
