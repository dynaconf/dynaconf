from __future__ import annotations

from dynaconf.typed import DictValue
from dynaconf.typed import Dynaconf
from dynaconf.typed import Options


class Person(DictValue):
    name: str
    teams: list


class Settings(Dynaconf):
    fruits: list
    colors: list = ["blue"]
    numbers: list = [1, 2, 3]

    # TODO: change this to use the Person class
    person: dict = {"name": "Bruno", "teams": ["dev"]}

    dynaconf_options = Options(
        envvar_prefix="INSERT_APP",
        settings_files=["settings.toml"],
        load_dotenv=True,
    )


settings = Settings()

expected_colors = [
    "red",  # comes from settings.toml
    "green",  # comes from .env
    "blue",  # comes from default init parameter
]

expected_teams = [
    "user",  # comes from .env
    "staff",  # comes from settings.toml
    "dev",  # comes from default init parameter
]

expected_roles = ["can_do_things"]  # comes from .env

expected_numbers = [
    42,  # comes from .env
    1,
    2,
    3,
]

expected_fruits = [
    "apple",  # comes from .env
]

assert settings.colors == expected_colors, settings.colors
assert settings.person.name == "Bruno", settings.person
assert settings.person.teams == expected_teams, settings.person.teams
assert settings.person.roles == expected_roles, settings.person.roles
assert settings.numbers == expected_numbers, settings.numbers
assert settings.fruits == expected_fruits, settings.fruits
