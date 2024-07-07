from typing import Optional

from dynaconf.typed import Annotated
from dynaconf.typed import DictValue
from dynaconf.typed import Dynaconf
from dynaconf.typed import ItemsValidator
from dynaconf.typed import NotRequired
from dynaconf.typed import Options
from dynaconf.typed import Validator
from dynaconf.typed.validators import Ge
from dynaconf.typed.validators import GenericValidator
from dynaconf.typed.validators import Gt
from dynaconf.typed.validators import is_connection_string
from dynaconf.typed.validators import is_url
from dynaconf.typed.validators import Le
from dynaconf.typed.validators import Lt
from dynaconf.typed.validators import Not
from dynaconf.typed.validators import Regex


class Database(DictValue):
    host: str
    port: int = 5432
    conn: NotRequired[Annotated[str, is_connection_string]]


class Plugin(DictValue):
    name: str
    version: str = "latest"


url_pattern = (
    r"((http|https)://)"  # Match the protocol (http or https) required
    r"(www\.)?"  # Match 'www.' optionally
    r"[\w.-]+"  # Match the domain name
    r"\.[a-z]{2,}"  # Match the top-level domain
    r"(/[^\s]*)?"  # Match the path (everything after the domain name)
)


class Interval(GenericValidator):
    operations = ["gt", "lt"]


class Settings(Dynaconf):
    title: Optional[str] = None
    api_prefix: Annotated[str, Validator(startswith="https://")]
    middlewares: Annotated[list[str], ItemsValidator(ne="deprecated.plugin")]
    static_url: Annotated[str, is_url]
    # not_a_url: Annotated[str, Not(IsUrl)] = "https://foo.bar"  # fails validation
    not_a_url: Annotated[str, Not(is_url)] = "batatinha 123"  # passes!
    version: Annotated[str, Regex(r"^(\d+)\.(\d+)\.(\d+)$")] = "3.1.9"
    database: Database = Database()
    flags: NotRequired[dict[str, bool]]
    plugins: list[Plugin] = []
    token: str
    number1: Annotated[int, Gt(1)] = 2
    number2: Annotated[int, Ge(4)] = 4
    number3: Annotated[int, Lt(4)] = 3
    number4: Annotated[int, Le(5)] = 5
    number5: Annotated[int, Interval(3, 90)] = 89
    # ^ same as Annotated[int, Gt(3), Lt(90)]

    dynaconf_options = Options(
        envvar_prefix="MYAPP",
        settings_files=["settings.toml", ".secrets.toml"],
        load_dotenv=True,
    )


settings = Settings(_debug_mode=True)
