from dynaconf import Dynaconf

settings = Dynaconf(**options)

assert settings.MESSAGE == "Hello from tmp"
print(settings.MESSAGE)  # noqa
