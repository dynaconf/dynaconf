from dynaconf import Dynaconf

settings = Dynaconf(**options)

assert settings.FIRST_VAR == "first_value"
assert settings.SECOND_VAR == "second_value"
assert settings.EXTRA_VAR == "extra_value"
