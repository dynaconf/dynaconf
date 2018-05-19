from dynaconf import LazySettings
settings = LazySettings(NAMESPACE_FOR_DYNACONF='example')

print(settings.USERNAME)
print(settings.SERVER)
print(settings.PASSWORD)
