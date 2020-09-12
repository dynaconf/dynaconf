REST_FRAMEWORK__DEFAULT_AUTHENTICATION_CLASSES = (
    "rest_framework.authentication.SessionAuthentication",
    "pulpcore.app.authentication.PulpRemoteUserAuthentication",
    "foo_bar1",
)
