from __future__ import annotations

import os

from dynaconf import Dynaconf

# ISSUE 794
# WHEN USING INCLUDES
# THE INCLUDES ARE LOADED RELATIVE TO
# THE FIRST LOADED FILE `conf/settings.toml`
settings = Dynaconf(
    settings_files=["conf/settings.toml", "conf/.secrets.toml"],
    includes=["**/*.toml"],
)

assert settings.a == 3
assert settings.b == 2
assert settings.included_host == "0.0.0.0"


# SO..
# WHEN USING INCLUDES IT IS RECOMMENDED
# TO SET THE ROOT PATH TO THE DIRECTORY
# WHERE THE SCRIPT IS RUNNING
# OR PASS AN ABSOLUTE PATH TO THE root_path or includes

HERE = os.path.dirname(os.path.abspath(__file__))
settings_with_root_path = Dynaconf(
    root_path=HERE,
    settings_files=["conf/settings.toml", "conf/.secrets.toml"],
    includes=["conf/**/*.toml"],
)

assert settings_with_root_path.a == 3
assert settings_with_root_path.b == 2
assert settings_with_root_path.included_host == "0.0.0.0"
