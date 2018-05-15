from dynaconf import settings
from dynaconf.loaders.vault_loader import writer

writer(settings, {'SECRET': 'vault_works'})
