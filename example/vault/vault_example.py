from dynaconf import settings
from dynaconf.loaders.vault_loader import load_keys

print(settings.SECRET)  # noqa
# >>> 'vault_works'


with settings.using_env("dev"):
    assert settings.SECRET == "vault_works_in_dev"

print(load_keys(settings, "test/"))
assert set(load_keys(settings, "test/")) == set(['default', 'dev'])
