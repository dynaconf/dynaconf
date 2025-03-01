import tomllib

from dynaconf.loaders.base import SourceMetadata


def load(settings, *args, **kwargs):
    """Load settings from pyproject.toml"""
    filepath = settings.find_file("pyproject.toml")
    if not filepath:
        return

    section_name = settings.get("pyproject_section", "pp_settings")
    with open(filepath, "rb") as open_file:
        pyproject_data = tomllib.load(open_file)
        tool_section = pyproject_data.get("tool", {})
        data = tool_section.get(section_name, {})

    if not data:
        return

    settings.update(
        data,
        loader_identifier=SourceMetadata(
            loader="pyproject_loader",
            identifier=filepath,
        ),
    )
    settings._loaded_files.append(filepath)
