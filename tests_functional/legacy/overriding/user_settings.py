# Alternative 1
# This works
# https://www.dynaconf.com/merging/#merging-existing-data-structures
from __future__ import annotations

REST_FRAMEWORK__DEFAULT_AUTHENTICATION_CLASSES = [
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.BasicAuthentication",
]  # noqa


# Alternative 2 (NOT IMPLEMENTED YET)
# TODO: Implement this merging override strategy

_REST_FRAMEWORK = {
    # Mark the `REST_FRAMEWORK` as a candidate for merging
    # specify the merge strategy for specific keys
    # strategies must be:
    # reset: clean existing value before reassign
    # merge: (the default) merge with existing values
    # unique: merge only if value doesn't already exists in the collection
    # conditional(expr): expression to evaluate as a conditional
    "dynaconf_merge": {
        "DEFAULT_AUTHENTICATION_CLASSES": {"strategy": "reset"}
        # ^ the key will be cleaned before assign new values
    },
    # Set keys you want to assign
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
}
