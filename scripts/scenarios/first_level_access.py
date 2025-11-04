"""
Dynaconf dot notation access scenario.

This scenario measures the performance of accessing Dynaconf settings
using dot notation (settings.key.subkey).
"""

LOOP_COUNT = 500_000
DATA = {"common": 123, "foo": True}


def baseline_setup():
    """Baseline setup function - creates raw dict for comparison."""
    data = DATA.copy()
    return {"data": data}


def baseline_run(context):
    """Baseline run function - performs raw dict access."""
    data = context["data"]
    for i in range(LOOP_COUNT):
        data["common"]


def setup():
    """Setup function - creates Dynaconf settings object."""
    from dynaconf import Dynaconf

    data = DATA.copy()
    settings = Dynaconf(**data)
    # Trigger setup to warm up the object
    settings.foo
    return {"settings": settings}


def run(context):
    """Run function - performs Dynaconf dot notation access."""
    settings = context["settings"]
    for i in range(LOOP_COUNT):
        settings.COMMON
