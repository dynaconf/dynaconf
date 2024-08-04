import warnings

from .exceptions import DynaconfSchemaError
from .exceptions import ValidationError
from .main import Dynaconf
from .main import Options
from .type_definitions import Annotated
from .type_definitions import DataDict
from .type_definitions import NotRequired
from .validators import ItemsValidator
from .validators import Validator

__all__ = [
    "Annotated",
    "DataDict",
    "Dynaconf",
    "DynaconfSchemaError",
    "ItemsValidator",
    "NotRequired",
    "Options",
    "Validator",
    "ValidationError",
]

warnings.warn(
    "dynaconf.typed module is on tech preview stage. "
    "The feature will be fully supported on dynaconf>=4.0.0. "
    "The feature works and is heavily tested however the APIs and "
    "usage are subject to change."
)
