from config import settings

assert settings.title == "My Awesome App"
assert settings.api_prefix == "https://my-great-api"
assert "admin" in settings.middlewares
assert settings.database.host == "postgres.com"
assert settings.database.port == 5433, settings.database.port
assert len(settings.plugins) == 3
assert settings.get("flags.power_mode") is True
assert settings.static_url.startswith("http")
assert settings.token is not None
