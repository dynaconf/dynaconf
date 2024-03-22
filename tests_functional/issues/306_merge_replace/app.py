from __future__ import annotations

from dynaconf import settings

EXPECTED = {
    "URL_FIELD_NAME": "pulp_href",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.LimitOffsetPagination"
    ),
    "PAGE_SIZE": 100,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "pulpcore.app.authentication.PulpRemoteUserAuthentication"
    ],
    "UPLOADED_FILES_USE_URL": False,
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "A_NESTED": {"LEVEL_ONE": {"LEVEL_TWO": {"FOO": [1, 2, 3, 4, 4]}}},
    "A_NEW_LIST": [5, 5, 5],
    "MERGE_A_LIST_UNIQUELY": [7, 8, 9, 10],
    "MERGE_A_LIST": [1, 2, 3, 4, 5, 6],
    "ANOTHER_THING": ["z"],
    "ANOTHER_THING_MERGED": ["a", "b", "c", "z"],
    "MERGE_A_DICT": {"a": 1, "b": 2},
    "A_DICT": {"ADD_KEY": 10, "EXISTING": 10},
}

assert (
    settings.REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES
    == EXPECTED["DEFAULT_AUTHENTICATION_CLASSES"]
), (
    settings.REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES,
    EXPECTED["DEFAULT_AUTHENTICATION_CLASSES"],
)

assert settings.REST_FRAMEWORK == EXPECTED, (settings.REST_FRAMEWORK, EXPECTED)


data = settings.REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES

assert len(data) == 1, (len(data), data)

assert data == [
    "pulpcore.app.authentication.PulpRemoteUserAuthentication"
], data
