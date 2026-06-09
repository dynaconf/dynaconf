from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import LazySettings


def test_multiple_yaml_environments_override(tmpdir):
    # Testing prod_yaml first, default_yaml second
    default_yaml = tmpdir.join("default.yaml")
    default_yaml.write("""
default:
  foo: "default_value"
""")

    prod_yaml = tmpdir.join("prod.yaml")
    prod_yaml.write("""
prod:
  foo: "prod_value"
""")

    settings = Dynaconf(
        settings_files=[str(prod_yaml), str(default_yaml)],
        environments=True,
        env="prod",
    )

    assert settings.get("foo") == "prod_value"


def test_multiple_yaml_environments_override_alternative_order(tmpdir):
    # Testing default_yaml first, prod_yaml second
    default_yaml = tmpdir.join("default.yaml")
    default_yaml.write("""
default:
  foo: "default_value"
""")

    prod_yaml = tmpdir.join("prod.yaml")
    prod_yaml.write("""
prod:
  foo: "prod_value"
""")

    settings = Dynaconf(
        settings_files=[str(default_yaml), str(prod_yaml)],
        environments=True,
        env="prod",
    )

    assert settings.get("foo") == "prod_value"


def test_multiple_yaml_environments_override_lazysettings(tmpdir):
    # Testing prod_yaml first, default_yaml second
    default_yaml = tmpdir.join("default_lazy.yaml")
    default_yaml.write("""
default:
  foo: "default_value"
""")

    prod_yaml = tmpdir.join("prod_lazy.yaml")
    prod_yaml.write("""
prod:
  foo: "prod_value"
""")

    settings = LazySettings(
        settings_files=[str(prod_yaml), str(default_yaml)],
        environments=True,
        ENV_FOR_DYNACONF="prod",
    )

    assert settings.get("foo") == "prod_value"
