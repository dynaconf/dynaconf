from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file=["settings.yaml"],
)

# spaced jeys can be accessed with dot notation by replacing
# spaces with underscores
assert settings.root.branch_node == "LEAF"
assert settings.root.BRANCH_node == "LEAF"
assert settings.root.banana_kid == 1

# however, the original keys are still available
assert settings.root == {"BANANA KID": 1, "BRANCH NODE": "LEAF"}
assert settings.root["BANANA KID"] == 1
assert settings.root["BRANCH NODE"] == "LEAF"
assert settings.root["branch NODE"] == "LEAF"
assert settings.first_name == "Bruno"
assert settings.first_NAME == "Bruno"
assert settings.FIRST_NAME == "Bruno"
assert settings["first_name"] == "Bruno"
assert settings["first name"] == "Bruno"
