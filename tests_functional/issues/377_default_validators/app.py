from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import Validator

settings = Dynaconf(
    validators=[Validator("COMPUTED", default=lambda st, va: "I am computed")]
)


assert settings.COMPUTED == "I am computed"

settings2 = Dynaconf(
    settings_file="settings.toml",
    environments=True,
    validators=[
        Validator(
            "FOO",
            env="production",
            default=lambda st, va: "FOO is computed in prod",
        ),
        Validator("BAR", env="production", default="@format {this.foo}/BAR"),
        Validator(
            "ZAZ", env="production", default="@jinja {{this.get('foo')}}/ZAZ"
        ),
        Validator("FOO", env="development", required=True, eq="dev foo"),
    ],
)

assert settings2.FOO == "dev foo"
assert settings2.get("FOO") == "dev foo"
assert settings2["FOO"] == "dev foo"
assert settings2.foo == "dev foo"
assert settings2("foo") == "dev foo"

assert settings2.from_env("production").FOO == "FOO is computed in prod"
assert settings2.from_env("production").foo == "FOO is computed in prod"
assert settings2.from_env("production")["FOO"] == "FOO is computed in prod"
assert settings2.from_env("production")("FOO") == "FOO is computed in prod"
assert settings2.from_env("production").get("FOO") == "FOO is computed in prod"

assert settings2.from_env("production").BAR == "FOO is computed in prod/BAR"
assert settings2.from_env("production").ZAZ == "FOO is computed in prod/ZAZ"
