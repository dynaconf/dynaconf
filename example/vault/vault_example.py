from dynaconf import settings

print(settings.SECRET)  # noqa
# >>> 'vault_works'


with settings.using_env("dev"):
    assert settings.SECRET == "vault_works_in_dev"
