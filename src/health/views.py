import logging
from urllib.request import urlopen

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse


def liveness(request: HttpRequest) -> HttpResponse:
    return HttpResponse('<img src="https://www.cjsr.com/wp-content/uploads/2017/06/itsalive.jpg" />')


def readiness(request: HttpRequest) -> JsonResponse:
    try:
        connection.connect()
    except Exception as e:
        logging.error(e)
        db_result = False
    else:
        db_result = True

    try:
        cache.set("check_health", "OK", 2)
    except Exception as e:
        logging.error(e)
        cache_result = False
    else:
        cache_result = cache.get("check_health") == "OK"

    try:
        resp = urlopen("https://suap.ifrn.edu.br/comum/solicitar_trocar_senha/", timeout=settings.DEFAULT_HTTP_TIMEOUT)
    except Exception as e:
        logging.error(e)
        suap_result = False
    else:
        suap_result = resp.getcode() == 200

    return JsonResponse(
        {
            "Database": db_result,
            "Cache": cache_result,
            "SUAP": suap_result,
            "Debug": settings.DEBUG,
            "ALL": db_result and cache_result and suap_result and settings.DEBUG,
        }
    )


def force_fail(request: HttpRequest) -> HttpResponse:
    raise Exception("Erro forçado para teste de monitoramento")


def force_db_fail(request: HttpRequest) -> HttpResponse:
    connection.connect()

    return HttpResponse("Pare o banco para forçar o erro.")
