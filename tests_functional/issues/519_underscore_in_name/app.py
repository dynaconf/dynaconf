from __future__ import annotations

import os

from dynaconf import Dynaconf

config = Dynaconf(
    settings_files=["settings.yml"],
    envvar_prefix="ATC",
    load_dotenv=True,
)

# envvar set is case insensitive
# ATC_BLE__DEVICE_ID=x and ATC_BLE__device_id=x are the same
expected = os.environ.get("EXPECTED_VALUE", 0)

# access is case insensitive
assert config.ble.device_id == int(expected)
assert config.BLE.DEVICE_ID == int(expected)
