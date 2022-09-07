from __future__ import annotations

import os

from dynaconf import Dynaconf

settings = Dynaconf()

# first we set something
os.environ["DYNACONF_SOMETHING"] = "this exists"

settings.get("FOO")  # this is just to fire the loaders

os.environ["DYNACONF_SOMETHING"] = "changed to other thing"

# then we load it freshly
assert settings.get_fresh("SOMETHING") == "changed to other thing"

# then we remove it from environment
del os.environ["DYNACONF_SOMETHING"]

assert "DYNACONF_SOMETHING" not in os.environ

# then we read it freshly again
assert settings.get_fresh("SOMETHING") is None, settings.get_fresh("SOMETHING")

settings.set("wm", "i3")

assert settings.WM == "i3"

settings.EDITOR = "vim"

assert settings.get("editor") == "vim"

assert settings.editor == "vim"

settings.terminal_emulator = "alacritty"

assert settings.get("TERMINAL_emulator") == "alacritty"

settings.set("a.b.c.d.e", "f")

# All the merging strategies

settings.set("a.b", {"other": 1, "dynaconf_merge": True})
settings.set("a.b", {"dynaconf_merge": {"another": 2}})
settings.set("a.b", "@merge {foo='bar'}", tomlfy=True)

assert settings.a == {
    "b": {"foo": "bar", "other": 1, "another": 2, "c": {"d": {"e": "f"}}}
}, settings.a

# Now the reset of a.b
settings.set("a__b", {"reset": None})

assert settings.a.b == {"reset": None}

settings.a.b.reset = 1

assert settings.A.b.reset == 1
