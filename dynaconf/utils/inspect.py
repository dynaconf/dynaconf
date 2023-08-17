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

from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.functional import empty
from dynaconf.vendor.box.box_list import BoxList
from dynaconf.vendor.ruamel.yaml import YAML

if TYPE_CHECKING:  # pragma: no cover
    from dynaconf.base import LazySettings, Settings


# Dumpers config

json_pretty = partial(json.dump, indent=2)
json_compact = json.dump

builtin_dumpers = {
    "yaml": YAML().dump,
    "json": json_pretty,
    "json-compact": json_compact,
}

OutputFormat = Union[Literal["yaml"], Literal["json"], Literal["json-compact"]]
DumperType = Callable[[dict, TextIO], None]


class KeyNotFoundError(Exception):
    pass


class EnvNotFoundError(Exception):
    pass


class OutputFormatError(Exception):
    pass


# Public


def inspect_settings(
    settings: Settings | LazySettings,
    key: str | None = None,
    env: str | None = None,
    new_first: bool = True,
    to_file: str = "",
    output_format: OutputFormat = "yaml",
    custom_dumper: DumperType | None = None,
    include_internal: bool = False,
    history_limit: int | None = None,
):
    """
    Print and return the loading history about a specific key path.
    Optionally, writes data to file in desired format instead.

    Args:
        settings: a Dynaconf instance
        key: string dotted path. E.g "path.to.key"
        ascending_order: if True, newest to oldest loading order
        fo_file: if specified, write to this filename
        output_format: available output format options
        custom_dumper: if provided, it is used instead of builtins
        include_internal: if True, include internal loaders (e.g. defaults)
                          This has effect only if key is not provided.
        history_limit: limits how many entries are shown
    """
    # get and process history
    original_settings = settings

    env_filter = None  # type: ignore
    if env:
        settings = settings.from_env(env)
        setting_envs = {
            _env.env for _env in settings._loaded_by_loaders.keys()
        }
        if env.lower() not in setting_envs:
            raise EnvNotFoundError(f"The requested env is not valid: {env!r}")

        def env_filter(src: SourceMetadata) -> bool:
            return src.env.lower() == env.lower()

    history = get_history(
        original_settings,
        key=key,
        filter_src_metadata=env_filter,
        include_internal=include_internal,
    )

    if new_first:
        history.reverse()

    if history_limit:
        history = history[:history_limit]

    if key:
        current_value = settings.get(key)
    else:
        current_value = settings.as_dict()

    # format output
    output_dict = {
        "header": {
            "env_filter": str(env),
            "key_filter": str(key),
            "new_first": str(new_first),
            "history_limit": str(history_limit),
            "include_internal": str(include_internal),
        },
        "current": current_value,
        "history": history,
    }

    output_dict["current"] = _ensure_serializable(output_dict["current"])

    # choose dumper
    try:
        dumper = builtin_dumpers[output_format.lower()]
    except KeyError:
        raise OutputFormatError(
            f"The desired format is not available: {output_format!r}"
        )

    dumper = dumper if not custom_dumper else custom_dumper

    # write to stdout or to file
    if not to_file:
        dumper(output_dict, sys.stdout)
    else:
        with open(
            to_file, "w", encoding=settings.get("ENCODER_FOR_DYNACONF")
        ) as f:
            dumper(output_dict, f)

    return output_dict


def get_history(
    obj: Settings | LazySettings,
    key: str | None = None,
    filter_src_metadata: Callable[[SourceMetadata], bool] | None = None,
    include_internal: bool = False,
    history_limit: int | None = None,
) -> list[dict]:
    """
    Gets data from `settings.loaded_by_loaders` in order of loading with
    optional filtering options.

    Returns a list of dict in new-first order, where the dict contains the
    data and it's source metadata.

    Args:
        obj: Setting object which contain the data
        key: dot-path to desired key. Use all if not provided
        filter_src_metadata: takes SourceMetadata and returns a boolean
        include_internal: if True, include internal loaders (e.g. defaults)
                          This has effect only if key is not provided.

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
            ...
        ]
    """
    if filter_src_metadata is None:

        def filter_src_metadata(src):
            return True

    sep = obj.get("NESTED_SEPARATOR_FOR_DYNACONF", "__")

    # trigger key based hooks
    if key:
        obj.get(key)  # noqa

    internal_identifiers = ["default_settings", "_root_path"]
    result = []
    for source_metadata, data in obj._loaded_by_loaders.items():
        # filter by source_metadata
        if filter_src_metadata(source_metadata) is False:
            continue

        # filter by internal identifiers
        if (
            not key
            and include_internal is False
            and source_metadata.identifier in internal_identifiers
        ):
            continue  # skip: internal loaders

        # filter by key path
        try:
            data = _get_data_by_key(data, key, sep=sep) if key else data
        except KeyError:
            continue  # skip: source doesn't contain the requested key

        # Normalize output
        data = _ensure_serializable(data)
        result.append({**source_metadata._asdict(), "value": data})

    if key and not result:
        # Key may be set in obj but history not tracked
        if (data := obj.get(key, empty)) is not empty:
            generic_source_metadata = SourceMetadata(
                loader="undefined",
                identifier="undefined",
            )
            data = _ensure_serializable(data)
            result.append({**generic_source_metadata._asdict(), "value": data})

        # Raise if still not found
        if key and not result:
            raise KeyNotFoundError(f"The requested key was not found: {key!r}")

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
        return data if isinstance(data, (int, bool, float)) else str(data)


def _get_data_by_key(
    data: dict,
    key_dotted_path: str,
    default: Any = None,
    sep="__",
):
    """
    Returns value found in data[key] using dot-path str (e.g, "path.to.key").
    Raises KeyError if not found
    """
    if not isinstance(data, DynaBox):
        data = DynaBox(data)  # DynaBox can handle insensitive keys
    if sep in key_dotted_path:
        key_dotted_path = key_dotted_path.replace(sep, ".")

    def traverse_data(data, path):
        # transform `a.b.c` in successive calls to `data['a']['b']['c']`
        path = path.split(".")
        root_key, nested_keys = path[0], path[1:]
        result = data[root_key]
        for key in nested_keys:
            result = result[key]
        return result

    try:
        return traverse_data(data, key_dotted_path)
    except KeyError:
        if not default:
            raise KeyError(f"Path not found in data: {key_dotted_path!r}")
        return default
