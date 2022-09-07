from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse


def index(request):
    tests = []
    tests.append("<b>.env</b>")
    tests.append(
        """<pre>DYNACONF_SERVER='prod_server_fromenv.com'
DEV_SERVER='dev_server_fromenv.com'
# switch envs or omit to default to DYNACONF
ENV_FOR_DYNACONF=dev
</pre>
    """
    )
    tests.append("<b>settings.toml</b>")
    tests.append(
        """<pre>[dynaconf]
server = 'foo.com'
username = 'prod user'
password = false  #  in prod this value must come from .secrets.toml or vault
STATIC_URL = '/changed/in/settings.toml/by/dynaconf/'

[dev]
username = 'dev user'</pre>
    """
    )
    tests.append("<b>.secrets.toml</b>")
    tests.append(
        """<pre>[dev]
password = 'My5up3r53c4et'</pre>
    """
    )

    tests.append(
        '<b>INSTALLED_APPS = ["dynaconf.contrib.django_dynaconf"...] </b>'
    )
    tests.append("<b> from django.conf import settings</b>")
    tests.append(f"settings.STATIC_URL: {settings.STATIC_URL}")
    tests.append(f"settings.SERVER: {settings.SERVER}")
    tests.append(f"settings.USERNAME: {settings.USERNAME}")
    tests.append(f"settings.PASSWORD: {settings.PASSWORD}")

    with settings.using_env("dev"):
        tests.append("<b>$ In dev env</b>")
        tests.append(f"settings.STATIC_URL: {settings.STATIC_URL}")
        tests.append(f"settings.SERVER: {settings.SERVER}")
        tests.append(f"settings.USERNAME: {settings.USERNAME}")
        tests.append(f"settings.PASSWORD: {settings.PASSWORD}")

    # settings.setenv('dev')
    return HttpResponse("<br>".join(tests))
