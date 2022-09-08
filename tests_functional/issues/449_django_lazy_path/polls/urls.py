from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [path("", views.index, name="index")]
