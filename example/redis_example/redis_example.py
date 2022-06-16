from __future__ import annotations

from dynaconf import settings

print(settings.FOO)  # noqa
# >>> 'foo_is_default'


with settings.using_env("development"):
    assert settings.SECRET == "redis_works_in_development", settings.SECRET
    assert settings.FOO == "foo_is_default"

available_envs = ["default", "development", "production"]
all_secrets = []

for env in available_envs:
    env_settings = settings.from_env(env)
    assert env_settings.SECRET == f"redis_works_in_{env}", env_settings.SECRET
    assert env_settings.FOO == "foo_is_default", env_settings.FOO
    all_secrets.append(env_settings.SECRET)

print(available_envs)
print(all_secrets)
