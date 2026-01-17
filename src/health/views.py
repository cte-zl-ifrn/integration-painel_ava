from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import connection
from django.core.cache import cache
from urllib.request import urlopen


def liveness(request: HttpRequest) -> HttpResponse:
    return HttpResponse('<img src="https://www.cjsr.com/wp-content/uploads/2017/06/itsalive.jpg" />')

def readiness(request: HttpRequest) -> JsonResponse:
    try:
        connection.connect()
    except:
        db_result = False
    else:
        db_result = True
        
    try:
        cache.set('check_health', 'OK', 2)
    except:
        cache_result = False
    else:
        cache_result = cache.get('check_health') == "OK"
        
    try:
        resp = urlopen("https://suap.ifrn.edu.br/comum/solicitar_trocar_senha/", timeout=2)
    except:
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
    1 / 0

def force_db_fail(request: HttpRequest) -> HttpResponse:
    # if not settings.DEBUG:
    #     return HttpResponse("OK")

    connection.connect()

    return HttpResponse("Pare o banco para forçar o erro.")
