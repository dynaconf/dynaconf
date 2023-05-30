"""Inspecting module"""
from __future__ import annotations

import sys
from typing import Any
from typing import Callable
from typing import TextIO
from typing import TYPE_CHECKING

from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.ruamel.yaml import YAML

if TYPE_CHECKING:
    from dynaconf.base import Settings


def inspect_key(setting, key_dotted_path: str):
    """
    Dumps loading history about a specific key (as dotted path)
    """
    print("[current-key-data]")
    print(f"- key: {repr(key_dotted_path)}")
    print(f"- value: {repr(setting.get(key_dotted_path))}")
    print(f"- env: {repr(setting.current_env)}")
    print("\n[loading-history]")
    dump_data_by_source(setting, key_dotted_path, ascendent_order=True)


DumperType = Callable[[dict, TextIO], None]


def dump_data_by_source(
    obj: Settings,
    key_dotted_path: str = "",
    ascendent_order: bool = True,
    dumper: DumperType = YAML().dump,
    output_stream: TextIO = sys.stdout,
):
    """
    Dumps data from `settings.loaded_by_loaders` in order of loading.

    Args:
        obj: Setting object which contain the data
        key_dotted_path: dot-path to desired key. Use all if not provided
        ascendent_order: if True, first loaded data goes on top
        dumper: function that can dump a dict with nested structures
        output_stream: where to dump (Eg. opened file, stdout, pipe)

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
    loaded_iter = (
        obj._loaded_by_loaders.items()
        if ascendent_order is True
        else reversed(obj._loaded_by_loaders.items())
    )
    order_count = 0 if ascendent_order else len(obj._loaded_by_loaders) + 1
    order_increment = 1 if ascendent_order else -1
    for source_metadata, data in loaded_iter:
        order_count += order_increment
        try:
            # filter by key or get all
            data = (
                get_data_by_key(data, key_dotted_path)
                if key_dotted_path
                else data
            )

            # DynaBox may cause serializing issues with the dumper
            data = dict(data) if isinstance(data, DynaBox) else data
        except KeyError:
            # skip, for this source does not contain the requested key
            continue

        output_data = {
            f"{order_count:02}": {**source_metadata._asdict(), "data": data}
        }
        dumper(output_data, output_stream)


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
