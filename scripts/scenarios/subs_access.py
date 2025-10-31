"""
Dynaconf subscript access scenario.

This scenario measures the performance of accessing Dynaconf settings
using subscript notation (settings["key"]["subkey"]).
"""

LOOP_COUNT = 100_000


def setup():
    """Setup function - creates Dynaconf settings object."""
    from dynaconf import Dynaconf

    data = {"common": {"mode": 123}}
    settings = Dynaconf(**data)
    # Trigger setup to warm up the object
    settings.common
    return {"settings": settings}


def run(context):
    """Run function - performs Dynaconf subscript access."""
    settings = context["settings"]
    for i in range(LOOP_COUNT):
        settings["common"]["mode"]
