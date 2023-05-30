"""Inspecting module"""
from __future__ import annotations

import sys
from typing import Any
from typing import Callable
from typing import Protocol
from typing import TextIO
from typing import TYPE_CHECKING

from dynaconf.loaders import yaml_loader
from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.box.box_list import BoxList
from dynaconf.vendor.ruamel.yaml import representer
from dynaconf.vendor.ruamel.yaml import YAML


class DumperType(Protocol):
    def __call__(self, data: dict, filename: str = "") -> None:
        ...


def yaml_dump(data: dict, filename: str = ""):
    """
    Write to stdout or to filename, if provided.

    Adaptor for dynaconf.loaders.yaml_loader:write
    """
    if filename:
        yaml_loader.write(filename, data, merge=False, mode="a")
    else:
        yaml_loader.dump(data)


if TYPE_CHECKING:
    from dynaconf.base import LazySettings, Settings


# Public


def inspect(
    settings: Settings | LazySettings,
    key_dotted_path: str = "",
    ascending_order: bool = True,
    format: str = "yaml",
    to_file: str = "",
):
    """
    Prints loading history about a specific key (as dotted path)
    Optionally, writes data to file in desired format instead.
    """
    # choose dumper
    if format.lower() == "yaml":
        dumper = yaml_dump
    else:
        raise ValueError(f"Unsupported format: {format}")

    # load current env data about key or all
    if key_dotted_path:
        try:
            current_data_dict = {
                "env": settings.current_env,
                "key": key_dotted_path,
                "value": settings.get(key_dotted_path),
            }
        except KeyError:
            # key not found
            raise
    else:
        current_data_dict = settings.as_dict()

    # write to stdout or to file
    if not to_file:
        print("[current-key-data]")
        dumper(current_data_dict)

        print("\n[loading-history]")
        _dump_data_loading_history(
            settings,
            key_dotted_path,
            ascendent_order=ascending_order,
            dumper=dumper,
        )
    else:
        dumper(current_data_dict, to_file)
        _dump_data_loading_history(
            settings,
            key_dotted_path,
            ascendent_order=ascending_order,
            dumper=dumper,
            filename=to_file,
        )


# Implementations


def ensure_serializable(data: BoxList | DynaBox) -> dict | list:
    """
    Converts box dict or list types to regular python dict or list
    Bypasses other values.
    """
    if isinstance(data, BoxList):
        return list(data)
    elif isinstance(data, DynaBox):
        return dict(data)
    else:
        return data


def _dump_data_loading_history(
    obj: Settings | LazySettings,
    key_dotted_path: str = "",
    ascendent_order: bool = True,
    dumper: DumperType = yaml_dump,
    filename: str = "",
):
    """
    Dumps all data from `settings.loaded_by_loaders` in order of loading.
    If @key_dotted_path is provided, filter by that key-path.

    Args:
        obj: Setting object which contain the data
        key_dotted_path: dot-path to desired key. Use all if not provided
        ascendent_order: if True, first loaded data goes on top
        dumper: function that can dump a dict with nested structures
        filename: filename to write. Dump to stdout otherwise


    Example:
        >>> settings = Dynaconf(...)
        >>> dump_data_loading_hitory(settings)
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
        dumper(output_data, filename)


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
