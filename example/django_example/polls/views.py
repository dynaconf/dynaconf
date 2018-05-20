from django.http import HttpResponse
from django.conf import settings


def index(request):
    tests = []
    tests.append('<b>.env</b>')
    tests.append("""<pre>DYNACONF_SERVER='prod_server_fromenv.com'
DEV_SERVER='dev_server_fromenv.com'
# switch namespaces or omit to default to DYNACONF
NAMESPACE_FOR_DYNACONF=dev
</pre>
    """)
    tests.append('<b>settings.toml</b>')
    tests.append("""<pre>[dynaconf]
server = 'foo.com'
username = 'prod user'
password = false
STATIC_URL = '/changed/in/settings.toml/by/dynaconf/'

[dev]
username = 'dev user'</pre>
    """)
    tests.append('<b>.secrets.toml</b>')
    tests.append("""<pre>[dynaconf]
password = 'My5up3r53c4et'</pre>
    """)

    tests.append(
        '<b>INSTALLED_APPS = ["dynaconf.contrib.django_dynaconf"...] </b>')
    tests.append('<b> from django.conf import settings</b>')
    tests.append(f"settings.STATIC_URL: {settings.STATIC_URL}")
    tests.append(f"settings.SERVER: {settings.SERVER}")
    tests.append(f"settings.USERNAME: {settings.USERNAME}")
    tests.append(f"settings.PASSWORD: {settings.PASSWORD}")

    # # Django threading is having problems with namespace switch
    # # using the .namespace method
    # with settings.using_namespace('dev'):
    #     tests.append('<b>$ In dev namespace</b>')
    #     tests.append(f"settings.STATIC_URL: {settings.STATIC_URL}")
    #     tests.append(f"settings.SERVER: {settings.SERVER}")
    #     tests.append(f"settings.USERNAME: {settings.USERNAME}")
    #     tests.append(f"settings.PASSWORD: {settings.PASSWORD}")

    # settings.namespace('dev')
    return HttpResponse(
        '<br>'.join(tests)
    )
