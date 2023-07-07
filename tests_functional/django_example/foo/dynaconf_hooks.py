from __future__ import annotations
import dynaconf


def post(settings):
    from django.urls import reverse_lazy  # noqa
    dynaconf.add_converter("reverse_lazy", reverse_lazy)

    data = {}
    data["HOOK_ON_DJANGO_APP"] = True
    return data
