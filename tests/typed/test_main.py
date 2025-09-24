from typing import Annotated
from typing import Optional
from typing import Union

from dynaconf.typed.type_definitions import DataDict
from dynaconf.typed.type_definitions import NotRequired
from dynaconf.typed.utils import dump_debug_info
from dynaconf.typed.validators import Contains


def test_extract():
    class Scheme(DataDict):
        part: str = "http"
        tls: bool = True

    class Link(DataDict):
        url: str = "/1"
        name: str
        scheme: Scheme
        data: dict = {1: 2}

    class Profile(DataDict):
        username: str = "um"
        team: int = 66
        avatar: str
        link: Link

    class Country(DataDict):
        name: str

    class State(DataDict):
        name: str
        country: Country

    class City(DataDict):
        name: str
        state: State

    class Person(DataDict):
        name: str = "Default Name"
        age: int
        profile: Profile
        profile2: Profile = {"username": "dois", "link": {"url": "/2"}}
        profile3: Profile = Profile(username="tres", link={"url": "/3"})
        profile4: Annotated[Profile, Contains("username")] = {}
        profile5: NotRequired[Profile] = {"avatar": "123"}
        profile6: Optional[Profile] = {}
        profile7: NotRequired[Profile]
        profiles: list[Profile] = [{"username": "l1"}, {}]
        profiles2: list[Profile] = []
        profiles3: list[Profile]
        maybe_profile: Union[int, Profile, float] = 1  # {"port": 199}
        dicted_profile: dict[str, Profile] = {
            "a": {"username": "dicted"},
            # "b": {},
        }
        city: City

    # print("PG", Person.__get_defaults__())

    # defaults, validators = extract_defaults_and_validators_from_typing(Person)
    # print()
    # print(defaults)
    # print(validators)

    # print()
    p = Person(
        {
            "name": "Juao",
            "age": 12,
            "profile": {
                "username": "Juao",
                "team": 10,
                "avatar": "juao.png",
                "link": {"url": "/juao", "name": "JuaoPageLink"},
            },
            "city": {
                "name": "Guararema",
                "state": {
                    "name": "Sao Paulo",
                    "country": {"name": "Brasil"},
                },
            },
        }
    )
    # print()
    # print("P", p)
    # print(p.profile.link.name)
    # print(p["profile"]["link"]["name"])
    # print(p.get("profile").get("link").get("name"))
    # print(p.city.name)
    # print(p["city"]["name"])
    # print(p.get("city").get("name"))
    # print(p.city.state.name)
    # print(p["city"]["state"]["name"])
    # print(p.get("city").get("state").get("name"))
    # print(p.city.state.country.name)
    # print(p["city"]["state"]["country"]["name"])
    # print(p.get("city").get("state").get("country").get("name"))
    #
    # p.city.state = {"name": "Bahia", "country": {"name": "BahiaZil"}}
    # print(p.city.state.name)
    # p.city.state.update({"name": "Ceara", "country": {"name": "CearaZil"}})
    # print(p.city.state.name)
    # print(p.city.state.country.name)
    # print(p["city"]["state"]["country"]["name"])
    # print(p.copy())

    dump_debug_info({}, [], p.__schema__)
    # for k, v in p.items():
    #     print(k, "=", v)
    # # print("#####")
    # # print(p.__defaults__)
    # print("#####")
    # for validator in p.__schema__.validators:
    #     print(validator)
    #     print()

    # print(p)
    # print(p.profile.link.scheme.part)
    # print(isinstance(p.profile.link, dict))
    # print(p["profile"].link["scheme"]["part"])
