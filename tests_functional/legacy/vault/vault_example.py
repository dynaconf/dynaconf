from __future__ import annotations

from dynaconf import settings
from dynaconf.loaders.vault_loader import list_envs
from dynaconf.loaders.vault_loader import write

print(settings.FOO)  # noqa
# >>> 'foo_is_default'


with settings.using_env("dev"):
    assert settings.SECRET == "vault_works_in_dev", settings.SECRET
    assert settings.FOO == "foo_is_default", settings.FOO

assert settings.SECRET == "vault_works_in_default"
available_envs = list_envs(settings, "dynaconf/")
assert set(available_envs) == {"default", "dev", "prod"}, available_envs

all_secrets = []

for env in available_envs:
    env_settings = settings.from_env(env)
    assert f"vault_works_in_{env}" == env_settings.from_env(env).SECRET
    assert env_settings.FOO == "foo_is_default"
    all_secrets.append(env_settings.SECRET)

print(available_envs)
print(all_secrets)

write(
    settings.from_env("prod"),
    {"SECRET": "vault_works_in_prod", "PROD_ONLY": "only_in_prod"},
)
dev_settings = settings.from_env("dev", VAULT_LOAD_ALL_ENVS_FOR_DYNACONF=False)
assert dev_settings.SECRET == "vault_works_in_dev"
assert dev_settings.FOO == "foo_is_default"
assert dev_settings.get("PROD_ONLY") is None
assert dev_settings.from_env("prod").PROD_ONLY == "only_in_prod"
