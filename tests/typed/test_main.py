from typing import Annotated
from typing import Optional
from typing import Union

# from dynaconf.typed.main import extract_defaults_and_validators_from_typing
from dynaconf.typed.types import DataDict
from dynaconf.typed.types import NotRequired
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

    class City(DataDict):
        name: str
        year: int

    class Person(DataDict):
        name: str = "a"
        port: int
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
        maybe_profile: Union[int, Profile, float] = {"port": 199}
        dicted_profile: dict[str, Profile] = {
            "a": {"username": "dicted"},
            "b": {},
        }
        city: City

    # print("PG", Person.__get_defaults__())

    # defaults, validators = extract_defaults_and_validators_from_typing(Person)
    # print()
    # print(defaults)
    # print(validators)

    # print()
    # p = Person()
    # print(p.__schema__.schema)
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
