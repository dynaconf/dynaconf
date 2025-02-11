from pathlib import Path
from textwrap import dedent

import pytest

from dynaconf import Dynaconf


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
