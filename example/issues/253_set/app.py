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
