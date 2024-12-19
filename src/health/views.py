from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.db import connection


def health(request: HttpRequest) -> HttpResponse:
    debug = "FAIL (are active)" if settings.DEBUG else "OK"

    try:
        connection.connect()
        connection_result = "OK"
    except:
        connection_result = "FAIL"

    return HttpResponse(
        f"""
        <pre>
            Reverse proxy: OK.
            Django: OK.
            Database: {connection_result}.
            Redis: Not tested.
            SUAP: Not tested.
            LDAP: Not tested.
            Debug: {debug}.
        </pre>
        """
    )

def force_fail(request: HttpRequest) -> HttpResponse:
    if not settings.DEBUG:
        return HttpResponse("OK")

    1 / 0

def force_db_fail(request: HttpRequest) -> HttpResponse:
    # if not settings.DEBUG:
    #     return HttpResponse("OK")

    connection.connect()

    return HttpResponse("Pare o banco para forçar o erro.")
