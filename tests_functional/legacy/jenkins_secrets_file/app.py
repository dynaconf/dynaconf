from __future__ import annotations

from dynaconf import settings

# Assuming this app is running on CI the secret values would be read from
# jenkins_secrets.toml that was  defined by SECRETS_FOR_DYNACONF envvar

assert settings.USERNAME == "jenkins"
assert settings.PASSWORD == "s3cr3t"
