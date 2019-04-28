import os

from dynaconf import settings

os.environ[
    "SETTINGS_FILE_FOR_DYNACONF"
] = "./cfg/default.toml,./cfg2/settings.toml"


print("development")
settings.setenv("development")
print(settings.VAR_DFT)
print(settings.VAR1)

print("changing to production")
settings.setenv("production")
print(settings.VAR1)

print("----")

print("development")
settings.setenv("development")
print(settings.VAR1)

print("changing to production")
settings.setenv("production")
print(settings.VAR1)


print("using only file 1")
os.environ["SETTINGS_FILE_FOR_DYNACONF"] = "./cfg/default.toml"

print("development")
settings.setenv("development")
print(settings.VAR_DFT)

print("changing to production")
settings.setenv("production")
print(settings.VAR_DFT)

print("----")


print("using only file 2")
os.environ["SETTINGS_FILE_FOR_DYNACONF"] = "./cfg2/settings.toml"

print("development")
settings.setenv("development")
print(settings.VAR1)

print("changing to production")
settings.setenv("production")
print(settings.VAR1)

print("----")
