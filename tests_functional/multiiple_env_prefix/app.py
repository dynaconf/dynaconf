from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="APP,OTHER,YET_ANOTHER,NOTUSED",
    load_dotenv=True,
)

assert settings.DATA.DB.host == "localhost"
assert settings.DATA.DB.port == 5432
assert settings.DATA.DB.user == "postgres"
