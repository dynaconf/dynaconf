from __future__ import annotations

import timeit
from textwrap import dedent

setup_code = """\
from dynaconf import Dynaconf
data = {"common": {"mode": 123}}
settings = Dynaconf(
    **data,
)
"""

repeats = 40_000
code = {
    "baseline": f"""\
        for i in range({repeats}):
            x = data["common"]["mode"]
        """,
    "dot_access": f"""\
        for i in range({repeats}):
            x = settings.common.mode
        """,
    "subs_access": f"""\
        for i in range({repeats}):
            x = settings["common"]["mode"]
        """,
}


def main():
    print(f"repeats: {repeats}")  # noqa
    for k, v in code.items():
        result = timeit.timeit(stmt=dedent(v), setup=setup_code, number=1)
        print(f"{k}: {result}")  # noqa


if __name__ == "__main__":
    main()
