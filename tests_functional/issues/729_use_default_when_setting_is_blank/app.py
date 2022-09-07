from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import Validator

settings = Dynaconf(
    settings_file="settings.yaml",
    validators=[
        Validator(
            "azurerm.client_secret",
            default="myAzurePass",
            apply_default_on_none=True,
        ),
    ],
)

assert (
    settings.azurerm.client_secret == "myAzurePass"
), settings.azurerm.client_secret
