
from dynaconf import settings


def test_has_wrapped():
    assert settings.configured is True
