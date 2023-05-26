from __future__ import annotations

from textwrap import dedent
from textwrap import indent
from typing import Any
from typing import Callable
from typing import TYPE_CHECKING

from django.utils.version import sys
from lark.utils import suppress

from dynaconf.vendor.ruamel import yaml

if TYPE_CHECKING:
    from dynaconf import Dynaconf
    from dynaconf.loaders.base import SourceMetadata


def inspect_key(setting, key_dotted_path: str):
    """
    Dumps loading history about a specific key (as dotted path)
    """
    print("[current-key-data]")
    print(f"- key: {repr(key_dotted_path)}")
    print(f"- value: {repr(setting.get(key_dotted_path))}")
    print(f"- env: {repr(setting.current_env)}")
    print("\n[loading-history]")
    dump_data_by_source(setting, key_dotted_path)


def dump_data_by_source(obj: Dynaconf, key_dotted_path: str = ""):
    """
    Dumps data from `settings.loaded_by_loaders` in order of loading.

    TODO:
        - Proper indent data with streams, not str return (see docs)
        - Add template system, maybe with jinja, so there can be presets
          and user-defined views

    Example:
        >>> settings = Dynaconf(...)
        >>> dump_data_by_source(settings)
        01:
            loader: yaml
            identifier: 'path/to/file.yml'
            env: default
            data:
                foo: bar
                spam: eggs
        02:
            loader: yaml
            identifier: 'path/to/file.yml'
            env: development
            data:
                foo: bar_from_dev
                spam: eggs_from_dev
        (...)
    """
    pad = "  "
    order_count = 0
    for source_metadata, data in obj._loaded_by_loaders.items():
        order_count += 1
        try:
            data = (
                get_data_by_key(data, key_dotted_path)
                if key_dotted_path
                else data
            )
        except KeyError:
            # this source does not contain the requested key
            continue
        print(f"{order_count:02}:")
        print(f"{pad}loaded_by: {repr(source_metadata.loader)}")
        print(f"{pad}identifier: {repr(source_metadata.identifier)}")
        print(f"{pad}environment: {repr(source_metadata.env)}")
        print(f"{pad}merged: {repr(source_metadata.merged)}")
        print(f"{pad}data:")
        # TODO docs don't recommended this. should indent streams directly
        print(
            indent(
                yaml.dump(data, Dumper=yaml.RoundTripDumper), prefix=pad * 2
            ),
            end="",
        )


def get_data_by_key(data: dict, key_dotted_path: str, default: Any = None):
    """
    Returns data in key
    Raises if not found
    """
    path = key_dotted_path.split(".")
    try:
        for node in path:
            if isinstance(data, dict):
                data = data[node.upper()]
            elif isinstance(data, list):
                data = data[int(node)]
    except (ValueError, IndexError, KeyError):
        if not default:
            raise KeyError(f"Path not found in data: {repr(key_dotted_path)}")
        return default
    return data
