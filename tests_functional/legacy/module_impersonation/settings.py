from __future__ import annotations

import sys

from dynaconf import Dynaconf

sys.modules[__name__] = Dynaconf(settings_files=["settings.toml"])
