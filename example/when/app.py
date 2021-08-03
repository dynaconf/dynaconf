"""
Issue: github.com/rochacbruno/dynaconf/issues/299#issuecomment-892104808
"""
from dynaconf import Dynaconf

settings = Dynaconf(
    PRELOAD_FOR_DYNACONF=["settings_from_plugin.py"],
    SETTINGS_FILE="settings_from_user.py",
    load_dotenv=False,
)

assert settings.COLORS == ["red", "green", "blue"], settings.COLORS
