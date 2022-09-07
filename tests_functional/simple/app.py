from __future__ import annotations

print("# Starting", __file__)
print("# On import level dynaconf will read .env and config envvars")
print("# It will also setup the initial search tree.")
print("\n")

from dynaconf import settings  # noqa

print("\n")
print("IS Dynaconf loaded yet?", settings.configured)
print("# ^ That means that no settings file was read yet! dynaconf is empty")
print("# Dynaconf is LAzy so it will load at the first access.")
print("# Lets make the first call to `settings.VALUE` watch the  logs...")
print("\n")
print(settings.VALUE)
print("\n")
print("# Now a second call to `settings.VALUE` already loaded:")
print("\n")
print(settings.VALUE)
print("\n")
print("IS Dynaconf loaded?", settings.configured)
print("# ^ That means that settings was read! dynaconf is loaded")
print("# Lets read a file using settings.find_file...")
print("\n")
with open(settings.find_file("settings.toml")) as settings_file:
    print(settings_file.read())

from dynaconf.utils.files import SEARCHTREE  # noqa

print("Searchtree", SEARCHTREE)
