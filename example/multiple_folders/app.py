from dynaconf import settings

print('development')
print(settings.VAR1)
print(settings.VAR2)

print('production')
settings.setenv('production')
print(settings.VAR1)
print(settings.VAR2)
