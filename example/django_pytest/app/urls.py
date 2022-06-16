from __future__ import annotations

from app import views
from django.urls import include
from django.urls import path

# namespacing
app_name = "app"

urlpatterns = [
    path(r"", views.HelloView.as_view(), name="hello"),
]
