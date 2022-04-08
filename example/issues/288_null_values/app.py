from dynaconf import Dynaconf

settings = Dynaconf(**options)

assert settings["NULLED_VALUE_PYTHON"] is None
assert settings["nulled_value_json"] is None
assert settings["nulled_value_yaml"] is None
assert settings["nulled_value_toml"] is None

print("#288 PASSED")
