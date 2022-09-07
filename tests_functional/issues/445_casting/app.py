from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(load_dotenv=True)

assert settings.get("UPSTREAM_ROOK.BUILD_ROOK_FROM_GIT") == "TRUE"

assert (
    settings.as_bool("UPSTREAM_ROOK.BUILD_ROOK_FROM_GIT") is True
), settings.as_bool("UPSTREAM_ROOK.BUILD_ROOK_FROM_GIT")

assert settings.get("UPSTREAM_ROOK__BUILD_ROOK_FROM_GIT", cast="@bool") is True
