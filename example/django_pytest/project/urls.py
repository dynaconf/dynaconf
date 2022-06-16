# https://docs.djangoproject.com/en/1.10/topics/http/urls/
from __future__ import annotations

from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path("", include("app.urls")),
    path("admin/", admin.site.urls),
]
