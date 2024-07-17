from typing import Annotated

from dynaconf.typed.main import extract_defaults_and_validators_from_typing
from dynaconf.typed.types import DictValue
from dynaconf.typed.types import NotRequired
from dynaconf.typed.validators import Contains


def test_extract():
    class Scheme(DictValue):
        part: str = "http"
        tls: bool = True

    class Link(DictValue):
        url: str
        name: str = "/linkname/"
        scheme: Scheme

    class Profile(DictValue):
        username: str = "foo"
        avatar: str
        link: Link

    class Person(DictValue):
        name: str = "a"
        port: int
        profile: Profile
        profile2: Profile = {"username": "dois"}
        profile3: Profile = Profile(username="tres", avatar="aaa")
        profile4: Annotated[Profile, Contains("name")] = {}
        alias: NotRequired[Profile] = {"avatar": "123"}

    # print("PG", Person.__get_defaults__())

    defaults, validators = extract_defaults_and_validators_from_typing(Person)
    # print()
    # print(defaults)
    # print(validators)

    p = Person(port=123)
    # print(p)
    p.profile.link.scheme.part
