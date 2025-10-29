from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf

base_dir = Path(__file__).parent / Path("folder")

settings = Dynaconf(settings_files=[base_dir / "settings.yaml"])
config = settings.__core__.config

# __import__("pdbr").set_trace()
settings.load_file(path=base_dir / Path("new.yaml"))

print(config.loaded_files)
assert len(config.loaded_files) == 2

assert settings.NAME == "Booba"
assert settings.NUMBER == 42
