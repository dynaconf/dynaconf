from dynaconf import settings
from dynaconf.loaders import vault_loader

vault_loader.write(settings, {'SECRET': 'vault_works'})

with settings.using_namespace('dev'):
    vault_loader.write(settings, {'SECRET': 'vault_works_in_dev'})
