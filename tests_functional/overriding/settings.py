from __future__ import annotations

REST_FRAMEWORK = {
    "URL_FIELD_NAME": "pulp_href",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPaginat",
    "PAGE_SIZE": 100,
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    # THE GOAL IS TO OVERRIDE THIS `DEFAULT_AUTHENTICATION_CLASSES` KEY
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # Keep this value
        "rest_framework.authentication.SessionAuthentication",
        # Remove this value
        "pulpcore.app.authentication.PulpRemoteUserAuthentication",
        # keep this value
        "rest_framework.authentication.BasicAuthentication",
    ),
    # Override is done in `user_settings.py`
    "UPLOADED_FILES_USE_URL": False,
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}
