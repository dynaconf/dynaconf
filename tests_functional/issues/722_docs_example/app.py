from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(envvar_prefix="PEANUT", load_dotenv=True)


assert settings.USER == "admin"
assert settings.PASSWD == 1234
assert settings.db.name == "foo"
assert settings.db.port == 2000
assert settings.db.scheme == "main"
