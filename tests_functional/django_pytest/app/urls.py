from __future__ import annotations

from django.urls import include
from django.urls import path

from app import views

# namespacing
app_name = "app"

urlpatterns = [
    path(r"", views.HelloView.as_view(), name="hello"),
]
