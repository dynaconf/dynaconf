from __future__ import annotations

from django.views.generic import TemplateView


class HelloView(TemplateView):
    template_name = "hello.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Hello!"
        context["message"] = "Hello world!"
        return context
