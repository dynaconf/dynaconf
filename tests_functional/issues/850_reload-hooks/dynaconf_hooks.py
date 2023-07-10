from __future__ import annotations


def post(settings):
    return {"counter": settings.counter + 1}
