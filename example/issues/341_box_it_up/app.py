from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(settings_file="settings.yaml")


all_days = settings.WEEK_DAYS


print(all_days)
