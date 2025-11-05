"""
Dynaconf setattr scenario.

This probably is not a realistic scenario, but provides some baseline of the
set overhead.
"""

LOOP_COUNT = 100_000


def baseline_setup():
    """Baseline setup function - creates raw dict for comparison."""
    data = {"common": 123}
    return {"data": data}


def baseline_run(context):
    """Baseline run function - performs raw dict access."""
    data = context["data"]
    for i in range(LOOP_COUNT):
        data["foo"] = 456


def setup():
    """Setup function - creates Dynaconf settings object."""
    from dynaconf import Dynaconf

    data = {"common": 123}
    settings = Dynaconf(**data)
    # Trigger setup to warm up the object
    settings.common
    return {"settings": settings}


def run(context):
    """Run function - performs Dynaconf dot notation access."""
    settings = context["settings"]
    for i in range(LOOP_COUNT):
        settings.foo = 456
