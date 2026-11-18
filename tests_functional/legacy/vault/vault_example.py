from __future__ import annotations

from dynaconf import settings
from dynaconf.loaders.vault_loader import list_envs

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

# Pin a KV v2 secret version: write a second revision of the default
# secret, then read the first one back through the pin.
from dynaconf import Dynaconf  # noqa
from dynaconf.loaders.vault_loader import write  # noqa


def kv2_settings(**extra):
    return Dynaconf(
        environments=True,
        VAULT_ENABLED_FOR_DYNACONF=True,
        VAULT_KV_VERSION_FOR_DYNACONF=2,
        VAULT_TOKEN_FOR_DYNACONF="myroot",
        **extra,
    )


write(kv2_settings(), {"SECRET": "vault_works_in_default_v2"})

latest = kv2_settings()
assert latest.SECRET == "vault_works_in_default_v2", latest.SECRET

pinned = kv2_settings(VAULT_SECRET_VERSION_FOR_DYNACONF=1)
assert pinned.SECRET == "vault_works_in_default", pinned.SECRET
print(f"pinned version 1: {pinned.SECRET} / latest: {latest.SECRET}")

# KV v1 keeps no versions: a pin combined with it must refuse, not
# silently read the latest.
try:
    Dynaconf(
        environments=True,
        VAULT_ENABLED_FOR_DYNACONF=True,
        VAULT_KV_VERSION_FOR_DYNACONF=1,
        VAULT_TOKEN_FOR_DYNACONF="myroot",
        VAULT_SECRET_VERSION_FOR_DYNACONF=1,
    ).SECRET
except ValueError as error:
    assert "keeps no secret versions" in str(error), error
else:
    raise AssertionError("a version pin on KV v1 must raise")
