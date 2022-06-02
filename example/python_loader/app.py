from dynaconf import Dynaconf

settings = Dynaconf(settings_file="setting.py", SILENT_ERRORS=False)

assert settings.FOO == "BAR"
