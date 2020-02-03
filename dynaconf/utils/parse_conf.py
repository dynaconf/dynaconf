import json
import os
from functools import wraps

import toml
from box import BoxKeyError

from dynaconf.utils.boxing import DynaBox

try:
    from jinja2 import Environment

    jinja_env = Environment()
    for p_method in ("abspath", "realpath", "relpath", "dirname", "basename"):
        jinja_env.filters[p_method] = getattr(os.path, p_method)
except ImportError:  # pragma: no cover
    jinja_env = None

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


class LazyFormat:
    """Holds data to format lazily."""

    dynaconf_lazy_format = True

    def __init__(self, value, formatter=str.format):
        self.value = value
        self.formatter = formatter

    @property
    def context(self):
        """Builds a context for formatting."""
        return {"env": os.environ, "this": self.settings}

    def __call__(self, settings):
        """LazyValue triggers format lazily."""
        self.settings = settings
        return self.formatter(self.value, **self.context)


def evaluate_lazy_format(f):
    """Marks a method on Settings instance to
    lazily evaluate LazyFormat objects upon access."""

    @wraps(f)
    def evaluate(settings, *args, **kwargs):
        value = f(settings, *args, **kwargs)
        if getattr(value, "dynaconf_lazy_format", None):
            return value(settings)
        return value

    return evaluate


def jinja_formatter(value, **context):
    if jinja_env is None:  # pragma: no cover
        raise ImportError(
            "jinja2 must be installed to enable '@jinja' settings in dynaconf"
        )
    return jinja_env.from_string(value).render(**context)


converters = {
    "@int": int,
    "@float": float,
    "@bool": lambda value: str(value).lower() in true_values,
    "@json": json.loads,
    "@format": lambda value: LazyFormat(value),
    "@jinja": lambda value: LazyFormat(value, formatter=jinja_formatter),
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
