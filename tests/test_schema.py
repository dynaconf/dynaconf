from dataclasses import dataclass

from dynaconf import Dynaconf
from dynaconf import Field
from dynaconf import Schema
from dynaconf import Validator


def test_schema(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        city: str
        name: str = Field()
        age: int = Field(18, validators=[Validator(gt=1, lt=16)])
        banana: str = Field()

    settings = Dynaconf(
        name="Bruno",
        city="São Paulo",
        BanAna=1,
        age=15,
        schema=MySchema,
    )

    assert settings.name == "Bruno"
    assert settings.age == 15
