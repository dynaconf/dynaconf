from dynaconf import settings

assert settings["NULL_VALUE_PYTHON"] is None
assert settings["nulled_value_json"] is None
assert settings["nulled_name"] is None
