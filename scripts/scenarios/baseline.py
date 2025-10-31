"""
Baseline scenario: Raw dict access without Dynaconf overhead.

This scenario measures the baseline performance of direct dictionary access
to establish a performance baseline for comparison with Dynaconf scenarios.
"""

LOOP_COUNT = 100_000


def setup():
    """Setup function - creates the basic data structure for testing."""
    data = {"common": {"mode": 123}}
    return {"data": data}


def run(context):
    """Run function - performs direct dictionary access."""
    data = context["data"]
    for i in range(LOOP_COUNT):
        data["common"]["mode"]
