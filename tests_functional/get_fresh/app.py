from __future__ import annotations

from dynaconf import settings
from dynaconf.loaders.toml_loader import write

# Get the potato
original = str(settings.POTATO)  # str() to force a copy
modern = "Modern Potato"
print("Original data:", original)
assert settings.POTATO == settings.get("potato") == original

# Change the Toml file
print("Change POTATO to `Modern Potato` in settings.toml file...")
write(settings.path_for("settings.toml"), {"default": {"potato": modern}})


# Print the original
print("Dynaconf knows:", settings.POTATO)
assert settings.POTATO == settings.get("potato") == original

# Get it freshly
print("Read it freshly to get changed value...")
print("Changed data:", settings.get_fresh("POTATO"))
assert settings.POTATO == settings.get_fresh("potato") == modern

# Get it again
print("Now read again without the get_fresh method")
print("Still the new value no?", settings.POTATO)
assert settings.POTATO == settings.get("potato") == modern

# Restore it
write(settings.path_for("settings.toml"), {"default": {"potato": original}})
