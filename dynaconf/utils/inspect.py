"""Inspecting module"""
from __future__ import annotations

import json
import sys
from functools import partial
from typing import Any
from typing import Callable
from typing import Literal
from typing import TextIO
from typing import TYPE_CHECKING
from typing import Union

from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.box.box_list import BoxList
from dynaconf.vendor.ruamel.yaml import YAML

if TYPE_CHECKING:
    from dynaconf.base import LazySettings, Settings
    from dynaconf.loaders.base import SourceMetadata


# Dumpers config

json_pretty = partial(json.dump, indent=2)
json_compact = json.dump

builtin_dumpers = {
    "yaml": YAML().dump,
    "json_pretty": json_pretty,
    "json_compact": json_compact,
}

OutputFormat = Union[
    Literal["yaml"], Literal["json_pretty"], Literal["json_compact"]
]
DumperType = Callable[[dict, TextIO], None]


# Public


def inspect_settings(
    settings: Settings | LazySettings,
    key_dotted_path: str = "",
    ascending_order: bool = True,
    to_file: str = "",
    output_format: OutputFormat = "yaml",
    custom_dumper: DumperType | None = None,
):
    """
    Prints loading history about a specific key (as dotted path string)
    Optionally, writes data to file in desired format instead.

    Args:
        settings: a Dynaconf instance
        key_dotted_path: string dotted path. E.g "path.to.key"
        ascending_order: if True, newest to oldest loading order
        fo_file: if specified, write to this filename
        output_format: available output format options
        custom_dumper: if provided, it is used instead of builtins
    """
    # choose dumper
    try:
        dumper = builtin_dumpers[output_format.lower()]
    except KeyError:
        raise ValueError(
            f"The desired format is not available: {output_format}"
        )

    dumper = dumper if not custom_dumper else custom_dumper

    # prepare output (current settings + history)
    history = get_history(settings)
    output_dict = {
        "header": {
            "current": {
                "env": settings.current_env,
                "key": key_dotted_path or "(all)",
                "value": settings.get(key_dotted_path)
                if key_dotted_path
                else settings.as_dict(),
            },
            "history_ordering": "ascending"
            if ascending_order
            else "descending",
        },
        "history": history if ascending_order else reversed(history),
    }
    output_dict["header"]["current"]["value"] = _ensure_serializable(
        output_dict["header"]["current"]["value"]
    )

    # write to stdout or to file
    if not to_file:
        dumper(output_dict, sys.stdout)
    else:
        with open(
            to_file, "w", encoding=settings.get("ENCODER_FOR_DYNACONF")
        ) as f:
            dumper(output_dict, f)


def get_history(
    obj: Settings | LazySettings,
    key_dotted_path: str = "",
    filter_src_metadata: Callable[[SourceMetadata], bool] = lambda x: True,
) -> list[dict]:
    """
    Gets data from `settings.loaded_by_loaders` in order of loading with
    optional filtering options.

    Returns a list of dict in ascending order, where the
    dict contains the data and it's source metadata.

    Args:
        obj: Setting object which contain the data
        key_dotted_path: dot-path to desired key. Use all if not provided
        filter_src_metadata: takes SourceMetadata and returns a boolean

    Example:
        >>> settings = Dynaconf(...)
        >>> get_history_data(settings)
        [
            {
                "loader": "yaml"
                "identifier": "path/to/file.yml"
                "env": "default"
                "data": {"foo": 123, "spam": "eggs"
            },
            {
                "loader": "yaml"
                "identifier": "path/to/file.yml"
                "env": "default"
                "data": {"foo": 123, "spam": "eggs"
            }
        ]
    """
    result = []
    for source_metadata, data in obj._loaded_by_loaders.items():
        # filter by source_metadata
        if filter_src_metadata(source_metadata) is False:
            continue

        # filter by key path
        try:
            data = (
                _get_data_by_key(data, key_dotted_path)
                if key_dotted_path
                else data
            )
        except KeyError:
            continue  # skip: source doesn't contain the requested key

        # Format output
        data = _ensure_serializable(data)
        result.append({**source_metadata._asdict(), "value": data})
    return result


def _ensure_serializable(data: BoxList | DynaBox) -> dict | list:
    """
    Converts box dict or list types to regular python dict or list
    Bypasses other values.
    {
        "foo": [1,2,3, {"a": "A", "b": "B"}],
        "bar": {"a": "A", "b": [1,2,3]},
    }
    """
    if isinstance(data, (BoxList, list)):
        return [_ensure_serializable(v) for v in data]
    elif isinstance(data, (DynaBox, dict)):
        return {
            k: _ensure_serializable(v) for k, v in data.items()  # type: ignore
        }
    else:
        return data


def _get_data_by_key(data: dict, key_dotted_path: str, default: Any = None):
    """
    Returns value found in data[key] using dot-path string (e.g, "path.to.key")
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
            raise KeyError(f"Path not found in data: {key_dotted_path!r}")
        return default
    return data
