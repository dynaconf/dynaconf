from dynaconf import Dynaconf

settings = Dynaconf(**options)

settings.configure(settings_module="/tmp/configure_test/settings.py")

assert settings.MESSAGE == "Hello from tmp"
print(settings.MESSAGE)  # noqa
