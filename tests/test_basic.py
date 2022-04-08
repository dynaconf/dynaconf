from dynaconf import Dynaconf

settings = Dynaconf(**options)


def test_has_wrapped():
    assert settings.configured is True
