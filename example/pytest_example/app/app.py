from dynaconf import Dynaconf

settings = Dynaconf(**options)


def return_a_value():
    return settings.VALUE


if __name__ == "__main__":
    assert return_a_value() == "On Default"
