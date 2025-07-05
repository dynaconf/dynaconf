from __future__ import annotations

from pyinstrument import Profiler


def test_dynaconf():
    from dynaconf import Dynaconf

    data = {"common": {"mode": 123}}
    settings = Dynaconf(
        **data,
    )

    for i in range(40000):
        settings.common.mode


def main():
    profiler = Profiler()
    profiler.start()
    test_dynaconf()
    profiler.stop()
    profiler.open_in_browser()
    return 0


if __name__ == "__main__":
    main()
