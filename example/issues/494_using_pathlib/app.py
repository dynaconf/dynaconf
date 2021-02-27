from pathlib import Path

from dynaconf import Dynaconf

base_dir = Path(__file__).parent / Path("folder")

settings = Dynaconf(settings_files=[base_dir / "settings.yaml"])

settings.load_file(path=base_dir / Path("new.yaml"))


assert settings.NAME == "Booba"
assert settings.NUMBER == 42
