from __future__ import annotations

import os

from dynaconf import settings

assert settings.get("FORMAT_USERNAME") is None
assert settings.DATABASE_NAME == "my_database.db"
assert os.environ["FORMAT_USERNAME"] == "robert_plant"

DB_PATH = "/home/robert_plant/databases/my_database.db"
assert settings.DATABASE_PATH == DB_PATH, settings.DATABASE_PATH
print(settings.DATABASE_PATH)


DB_PATH_JINJA = "/home/robert_plant/development/my_database.db"
assert (
    settings.DATABASE_PATH_JINJA == DB_PATH_JINJA
), settings.DATABASE_PATH_JINJA
print(settings.DATABASE_PATH_JINJA)
