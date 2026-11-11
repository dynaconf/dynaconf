from pathlib import Path
from textwrap import dedent

import pytest

from dynaconf import Dynaconf

pytestmark = pytest.mark.usefixtures("no_deprecations")


@pytest.fixture
def file_factory(tmp_path: Path):
    """Fixture to create a file in pytest tmpdir."""

    def create_file(filename: str, content: str) -> str:
        filepath = tmp_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(dedent(content))
        return str(filepath.absolute())

    return create_file


@pytest.mark.parametrize("silent", [True, False])
@pytest.mark.parametrize(
    "filename", ["f.yml", "f.toml", "f.ini", "f.py", "f.json"]
)
def test_loaders_raise_on_syntax_error(file_factory, filename, silent):
    """When dynaconf tries to load a file with syntax error, an error is raised."""
    # invalid syntax for any file format
    filepath = file_factory(filename, "asdf")

    # assert on initialization
    with pytest.raises(Exception):
        settings = Dynaconf(settings_files=filepath, silent=silent)
        settings.as_dict()

    # assert on explicit load call
    settings = Dynaconf()
    with pytest.raises(Exception):
        settings.load_file(path=filepath, silent=silent)


@pytest.fixture(
    params=[
        (
            "toml",
            '[development]\nvalue = "loaded"\n[extra]\nother = "extra"\n',
        ),
        (
            "json",
            '{"development": {"value": "loaded"}, '
            '"extra": {"other": "extra"}}',
        ),
        (
            "yaml",
            "development:\n  value: loaded\nextra:\n  other: extra\n",
        ),
        (
            "ini",
            "[development]\nvalue = loaded\n[extra]\nother = extra\n",
        ),
    ],
    ids=["toml", "json", "yaml", "ini"],
)
def environment_file(request, file_factory):
    extension, content = request.param
    return file_factory(f"settings.{extension}", content)


@pytest.mark.parametrize(
    "default_env, envvar_prefix",
    [
        ("default", "APP"),
        ("development", "APP"),
        ("development", "development"),
    ],
    ids=["missing-default", "missing-prefix", "missing-global"],
)
def test_strict_load_skips_missing_fallbacks(
    environment_file, default_env, envvar_prefix
):
    settings = Dynaconf(
        settings_files=[environment_file],
        environments=True,
        env="DEVELOPMENT",
        default_env=default_env,
        envvar_prefix=envvar_prefix,
        silent_errors=False,
    )

    assert settings.value == "loaded"


@pytest.mark.parametrize(
    "env, missing",
    [
        ("MISSING", "missing"),
        ("GLOBAL", "global"),
        ("DEVELOPMENT, MISSING", "missing"),
    ],
)
def test_strict_load_reports_missing_requested_environment(
    environment_file, env, missing
):
    settings = Dynaconf(
        settings_files=[environment_file],
        environments=True,
        env=env,
        envvar_prefix="APP",
        silent_errors=False,
    )

    with pytest.raises(KeyError) as exc_info:
        settings.as_dict()
    assert exc_info.value.args == (missing,)


def test_strict_load_multiple_requested_environments(environment_file):
    settings = Dynaconf(
        settings_files=[environment_file],
        environments=True,
        env="DEVELOPMENT, EXTRA",
        silent_errors=False,
    )

    assert settings.value == "loaded"
    assert settings.other == "extra"


def test_strict_load_file_uses_requested_environment(environment_file):
    settings = Dynaconf(settings_files=[], environments=True, env="production")

    settings.load_file(environment_file, env="development", silent=False)

    assert settings.value == "loaded"
