from __future__ import annotations


def post(settings):
    data = {"dynaconf_merge": True}
    if settings.get("ADD_BEATLES") is True:
        data["BANDS"] = ["Beatles"]
    return data
