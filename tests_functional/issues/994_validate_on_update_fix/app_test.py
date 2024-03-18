"""
#994 (https://github.com/dynaconf/dynaconf/issues/994)


"""

from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import Validator


def test_994():
    settings = Dynaconf(
        settings_files=["veryeasyfatt.config.toml", ".secrets.toml"],
        # Merge all found files into one configuration.
        merge_enabled=True,
        # Validate the configuration when it is updated.
        validate_on_update=True,
        validators=[  # Custom validators.
            Validator(
                "files.output.kml",
                default="output.kml",
            ),
        ],
    )

    # Setup default values for missing settings (see #993)
    if str(settings.files.output.kml.strip()) == "":
        settings.files.output.kml = "output.kml"

    assert settings.files.output.kml


def test_minimal():
    settings = Dynaconf(
        merge_enabled=True,
        validate_on_update=True,
        validators=[Validator("foo", must_exist=True, default="none")],
    )
    settings.set("foo", "bar")
    assert settings
