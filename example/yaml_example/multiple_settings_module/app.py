from dynaconf import settings

#It will raise MultipleConfigFileError because there are multiple config files on root
print(settings.HOST)
print(settings.PORT)
print(settings.USERNAME)
print(settings.PASSWORD)
print(settings.LEVELS)
print(settings.TEST_LOADERS)
print(settings.MONEY)
print(settings.AGE)
print(settings.ENABLED)

