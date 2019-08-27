from dynaconf import settings
from dynaconf.loaders.vault_loader import list_envs

print(settings.SECRET)  # noqa
# >>> 'vault_works'


with settings.using_env("dev"):
    assert settings.SECRET == "vault_works_in_dev"

assert set(list_envs(settings, "dynaconf/")) == set(["default", "dev"])
