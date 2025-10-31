from __future__ import annotations

from pyinstrument import Profiler


def setup_dynaconf():
    from dynaconf import Dynaconf

    data = {"common": {"mode": 123}}
    settings = Dynaconf(
        **data,
    )
    settings.common  # trigger setup
    return settings


def setup_datadict():
    from dynaconf.nodes import DataDict

    return DataDict({"common": {"mode": 123}})


def test_scenario(settings):
    for i in range(500_000):
        settings["common"]["mode"]


def main():
    profiler = Profiler()
    obj = setup_dynaconf()
    profiler.start()
    test_scenario(obj)
    profiler.stop()
    profiler.open_in_browser()
    return 0


if __name__ == "__main__":
    main()
