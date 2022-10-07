from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="ISSUE726",
    settings_files=["defaults.yaml", "configuration.yaml"],
    merge_enabled=True,
)


assert settings.config_key.nested_list == [
    "item_a",
    "item_b",
    "item_c",
], settings.config_key.nested_list
