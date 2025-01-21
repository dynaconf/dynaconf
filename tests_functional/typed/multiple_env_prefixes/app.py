from __future__ import annotations

from dynaconf.typed import Dynaconf
from dynaconf.typed import Options


class Settings(Dynaconf):
    dynaconf_options = Options(
        envvar_prefix="APP,OTHER,YET_ANOTHER,NOTUSED",
        load_dotenv=True,
    )


settings = Settings()

assert settings.DATA.DB.host == "localhost"
assert settings.DATA.DB.port == 5432
assert settings.DATA.DB.user == "postgres"
