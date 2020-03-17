import json
import os
import re
import warnings
from functools import wraps

import toml
from box import BoxKeyError

from dynaconf.utils import extract_json_objects
from dynaconf.utils import multi_replace
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


KV_PATTERN = re.compile(r"([a-zA-Z0-9 ]*=[a-zA-Z0-9\- :]*)")
"""matches `a=b, c=d, e=f` used on `VALUE='@merge foo=bar'` variables."""


class DynaconfParseError(Exception):
    """Error to raise when parsing @casts"""


class MetaValue:
    """A Marker to trigger specific actions on `set` and `object_merge`"""

    _meta_value = True

    def __init__(self, value):
        self.value = parse_conf_data(value, tomlfy=True)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value}) on {id(self)}"

    def unwrap(self):
        return self.value


class Reset(MetaValue):
    """Triggers an existing key to be reset to its value
    NOTE: DEPRECATED on v3.0.0
    """

    _dynaconf_reset = True

    def __init__(self, value):
        self.value = parse_conf_data(value, tomlfy=True)
        warnings.warn(f"{self.value} does not need `@reset` anymore.")


class Del(MetaValue):
    """Triggers an existing key to be deleted"""

    _dynaconf_del = True

    def unwrap(self):
        raise ValueError("Del object has no value")


class Merge(MetaValue):
    """Triggers an existing key to be merged"""

    _dynaconf_merge = True

    def __init__(self, value, unique=False):

        self.value = parse_conf_data(value, tomlfy=True)

        if isinstance(self.value, (int, float, bool)):
            # @merge 1, @merge 1.1, @merge False
            self.value = [self.value]
        elif isinstance(self.value, str):
            # @merge {"valid": "json"}
            json_object = list(
                extract_json_objects(
                    multi_replace(
                        self.value,
                        {
                            ": True": ": true",
                            ":True": ": true",
                            ": False": ": false",
                            ":False": ": false",
                            ": None": ": null",
                            ":None": ": null",
                        },
                    )
                )
            )
            if len(json_object) == 1:
                self.value = json_object[0]
            else:
                matches = KV_PATTERN.findall(self.value)
                # a=b, c=d
                if matches:
                    self.value = {
                        k.strip(): parse_conf_data(v, tomlfy=True)
                        for k, v in (
                            match.strip().split("=") for match in matches
                        )
                    }
                elif "," in self.value:
                    # @merge foo,bar
                    self.value = self.value.split(",")
                else:
                    # @merge foo
                    self.value = [self.value]

        self.unique = unique


class BaseFormatter:
    def __init__(self, function, token):
        self.function = function
        self.token = token

    def __call__(self, value, **context):
        return self.function(value, **context)

    def __str__(self):
        return str(self.token)


def _jinja_formatter(value, **context):
    if jinja_env is None:  # pragma: no cover
        raise ImportError(
            "jinja2 must be installed to enable '@jinja' settings in dynaconf"
        )
    return jinja_env.from_string(value).render(**context)


class Formatters:
    """Dynaconf builtin formatters"""

    python_formatter = BaseFormatter(str.format, "format")
    jinja_formatter = BaseFormatter(_jinja_formatter, "jinja")


class Lazy:
    """Holds data to format lazily."""

    _dynaconf_lazy_format = True

    def __init__(self, value, formatter=Formatters.python_formatter):
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

    def __str__(self):
        """Gives string representation for the object."""
        return str(self.value)

    def __repr__(self):
        """Give the quoted str representation"""
        return f"'@{self.formatter} {self.value}'"

    def _dynaconf_encode(self):
        """Encodes this object values to be serializable to json"""
        return f"@{self.formatter} {self.value}"


def try_to_encode(value, callback=str):
    """Tries to encode a value by verifying existence of `_dynaconf_encode`"""
    try:
        return value._dynaconf_encode()
    except (AttributeError, TypeError) as e:
        return callback(value)


def evaluate_lazy_format(f):
    """Marks a method on Settings instance to
    lazily evaluate LazyFormat objects upon access."""

    @wraps(f)
    def evaluate(settings, *args, **kwargs):
        value = f(settings, *args, **kwargs)
        if getattr(value, "_dynaconf_lazy_format", None):
            return value(settings)
        return value

    return evaluate


converters = {
    "@int": int,
    "@float": float,
    "@bool": lambda value: str(value).lower() in true_values,
    "@json": json.loads,
    "@format": lambda value: Lazy(value),
    "@jinja": lambda value: Lazy(value, formatter=Formatters.jinja_formatter),
    # Meta Values to trigger pre assignment actions
    "@reset": lambda value: Reset(value),  # @reset is DEPRECATED on v3.0.0
    "@del": lambda value: Del(value),
    "@merge": lambda value: Merge(value),
    "@merge_unique": lambda value: Merge(value, unique=True),
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
        return toml.loads(f"key={data}", DynaBox).key
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
    elif isinstance(value, Lazy):
        return try_to_encode(value)
    elif value is None:
        return "@none "
    else:
        return value
