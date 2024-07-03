import re
from typing import Optional

from dynaconf.typed import Annotated
from dynaconf.typed import DictValue
from dynaconf.typed import Dynaconf
from dynaconf.typed import ItemsValidator
from dynaconf.typed import NotRequired
from dynaconf.typed import Options
from dynaconf.typed import Validator


class Database(DictValue):
    host: str
    port: int = 5432


class Plugin(DictValue):
    name: str
    version: str = "latest"


url_pattern = re.compile(
    r"((http|https)://)"  # Match the protocol (http or https) required
    r"(www\.)?"  # Match 'www.' optionally
    r"[\w.-]+"  # Match the domain name
    r"\.[a-z]{2,}"  # Match the top-level domain
    r"(/[^\s]*)?"  # Match the path (everything after the domain name)
)


class Settings(Dynaconf):
    title: Optional[str] = None
    api_prefix: Annotated[str, Validator(startswith="https://")]
    middlewares: Annotated[
        list[str], ItemsValidator(Validator(ne="deprecated.plugin"))
    ]
    static_url: Annotated[str, Validator(condition=url_pattern.match)]
    database: Database
    flags: NotRequired[dict[str, bool]]
    plugins: list[Plugin] = []
    token: str

    dynaconf_options = Options(
        envvar_prefix="MYAPP",
        settings_files=["settings.toml", ".secrets.toml"],
        load_dotenv=True,
    )


settings = Settings()
