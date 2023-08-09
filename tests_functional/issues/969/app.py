from __future__ import annotations

from dynaconf import Dynaconf

data = {1: 2}
settings = Dynaconf()

# __import__('ipdb').set_trace()
settings.set("data", data)


assert settings["data"][1] == 2
