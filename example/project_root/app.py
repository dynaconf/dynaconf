from dynaconf import settings

assert settings.MESSAGE == "Hello from tmp"
print(settings.MESSAGE)  # noqa
