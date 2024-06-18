from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf

settingsenv = Dynaconf(environments=True)
settings = Dynaconf(
    TEST_KEY="test_value",
    ANOTHER_KEY="another_value",
    DATA={"KEY": "value", "OTHERKEY": "other value"},
    A_PATH=Path("foo"),
)
