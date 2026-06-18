from __future__ import annotations

import pytest
from dynaconf import Dynaconf

@pytest.mark.parametrize(
    "order",
    [
        ("default", "prod"),
        ("prod", "default"),
    ],
    ids=["default_first", "prod_first"]
)
@pytest.mark.parametrize("default_ext", ["yaml", "toml", "json"])
@pytest.mark.parametrize("prod_ext", ["yaml", "toml", "json"])
def test_multiple_environments_override(
    create_file, default_ext, prod_ext, order
):
    if default_ext != prod_ext and order == ("prod", "default"):
        pytest.xfail("Dynaconf sequentially evaluates loaders, breaking env precedence for mixed formats loaded in prod_first order")

    default_content = {
        "yaml": "default:\n  foo: 'default_value'\n",
        "toml": "[default]\nfoo = 'default_value'\n",        "json": '{"default": {"foo": "default_value"}}',
    }[default_ext]
    
    prod_content = {
        "yaml": "prod:\n  foo: 'prod_value'\n",
        "toml": "[prod]\nfoo = 'prod_value'\n",
        "json": '{"prod": {"foo": "prod_value"}}',
    }[prod_ext]

    default_file = create_file(f"default.{default_ext}", default_content)
    prod_file = create_file(f"prod.{prod_ext}", prod_content)

    files = [
        str(default_file) if f == "default" else str(prod_file)
        for f in order
    ]

    settings = Dynaconf(
        settings_files=files,
        environments=True,
        env="prod",
    )

    assert settings.get("foo") == "prod_value"
