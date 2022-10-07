from __future__ import annotations

import pytest
from config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    assert settings.current_env == "testing"


def test_running_on_testing_environment():
    assert settings.current_env == "testing"
    assert settings.ENV_FOR_DYNACONF == "testing"
    assert settings.NAME == "testing name"
