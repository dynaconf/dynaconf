from dynaconf import settings
from dynaconf.loaders import vault_loader

vault_loader.write(settings, {'SECRET': 'vault_works'})
