from __future__ import annotations

import dynaconf


def post(settings):
    return {"HOOK_ON_DJANGO_APP": True}
