from __future__ import annotations

from dynaconf import settings


def return_a_value():
    return settings.VALUE


if __name__ == "__main__":
    assert return_a_value() == "On Default"
