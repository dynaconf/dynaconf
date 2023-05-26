from __future__ import annotations

from textwrap import indent
from typing import TYPE_CHECKING

from django.utils.version import sys

from dynaconf.vendor.ruamel import yaml

if TYPE_CHECKING:
    from dynaconf import Dynaconf
    from dynaconf.loaders.base import SourceMetadata


def dump_data_by_source(obj: Dynaconf):
    """
    Dumps data from `settings.loaded_by_loaders` in order of loading.

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
    print()
    pad = "  "
    order_count = 0
    for source_metadata, data in obj.loaded_by_loaders.items():
        order_count += 1
        print(f"{order_count:02}:")
        print(f"{pad}loader: {repr(source_metadata.loader)}")
        print(f"{pad}identifier: {repr(source_metadata.identifier)}")
        print(f"{pad}environment: {repr(source_metadata.env)}")
        print(f"{pad}data:")
        # TODO docs says this is not recommended. See how to indent the streams directly
        print(indent(yaml.dump(data, Dumper=yaml.RoundTripDumper), prefix=pad * 2), end="")
