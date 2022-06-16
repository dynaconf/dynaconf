# Covering this issue: https://pulp.plan.io/issues/6244
from __future__ import annotations

REST_FRAMEWORK = {
    "URL_FIELD_NAME": "pulp_href",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.LimitOffsetPagination"
    ),
    "PAGE_SIZE": 100,
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "foo",
        "bar",
        "zaz",
    ),
    "ANOTHER_THING": ("a", "b", "c"),
    "ANOTHER_THING_MERGED": ("a", "b", "c"),
    "UPLOADED_FILES_USE_URL": False,
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "MERGE_A_LIST": [1, 2, 3],
    "MERGE_A_LIST_UNIQUELY": [7, 8, 9],
    "A_NESTED": {"LEVEL_ONE": {"LEVEL_TWO": {"FOO": [1, 2, 3]}}},
    "MERGE_A_DICT": {"b": 2},
    "A_DICT": {"EXISTING": 10},
}
