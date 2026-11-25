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


@pytest.mark.parametrize(
    "filename,content",
    [
        (
            "settings.toml",
            """\
            [default]
            db = { host = "localhost", port = 5432 }

            [development]
            debug = true
            db = { host = "devdb", dynaconf_merge = true }
            """,
        ),
        (
            "settings.yaml",
            """\
            default:
              db:
                host: localhost
                port: 5432
            development:
              debug: true
              db:
                host: devdb
                dynaconf_merge: true
            """,
        ),
        (
            "settings.json",
            """\
            {
              "default": {"db": {"host": "localhost", "port": 5432}},
              "development": {
                "debug": true,
                "db": {"host": "devdb", "dynaconf_merge": true}
              }
            }
            """,
        ),
    ],
)
def test_write_preserves_dynaconf_merge_tokens(
    file_factory, filename, content
):
    """Writing to a file must not consume `dynaconf_merge` tokens already
    present in it, otherwise the environment loses the inherited keys.
    Regression test for https://github.com/dynaconf/dynaconf/issues/1467
    """
    from dynaconf.loaders import write

    filepath = file_factory(filename, content)
    write(
        filename=filepath,
        data={"development": {"NEWKEY": 42}},
        merge=True,
    )

    with open(filepath, encoding="utf-8") as f:
        assert "dynaconf_merge" in f.read()

    # the inherited keys must survive a write round-trip
    settings = Dynaconf(settings_files=filepath, environments=True)
    assert settings.DB == {"host": "devdb", "port": 5432}
    assert settings.NEWKEY == 42


def test_write_preserves_merge_tokens_in_lists(file_factory):
    """`dynaconf_merge` inside lists must also survive a write round-trip."""
    from dynaconf.loaders import write

    filepath = file_factory(
        "settings.toml",
        """\
        [default]
        plugins = ["a", "b"]

        [development]
        plugins = ["c", "dynaconf_merge"]
        """,
    )
    write(
        filename=filepath,
        data={"development": {"NEWKEY": 42}},
        merge=True,
    )

    with open(filepath, encoding="utf-8") as f:
        assert "dynaconf_merge" in f.read()

    settings = Dynaconf(settings_files=filepath, environments=True)
    assert settings.PLUGINS == ["a", "b", "c"]
