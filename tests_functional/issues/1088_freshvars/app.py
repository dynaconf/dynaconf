from __future__ import annotations

import os
from pathlib import Path

from dynaconf import Dynaconf

HERE = Path(__file__).parent

os.environ["DYNACONF_NAME"] = "stay fresh"
settings = Dynaconf(
    fresh_vars=["name", "AGE"], settings_files=["settings.toml"]
)


def do_the_sets(age: int = 10):
    with open(HERE / "settings.toml", "w") as sf:
        sf.write(f"age = {age}")

    settings.name = "not so fresh"  # NO EFFECT
    settings.NAME = "not so fresh"
    settings.NaMe = "not so fresh"
    settings.set("name", "not so fresh")
    settings["name"] = "not so fresh"

    print(settings.name)
    print(settings.age)


do_the_sets()
assert settings["NAME"] == "stay fresh"
assert settings["AGE"] == 10
do_the_sets(20)
assert settings.name == "stay fresh"
assert settings["AGE"] == 20
do_the_sets(30)
assert settings.NAME == "stay fresh"
assert settings["AGE"] == 30
do_the_sets(40)
assert settings["NAME"] == "stay fresh"
assert settings["AGE"] == 40
do_the_sets(50)
assert settings("NAME") == "stay fresh"
assert settings["AGE"] == 50
