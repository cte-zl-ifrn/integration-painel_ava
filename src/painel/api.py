from ninja import NinjaAPI
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from a4.models import logged_user
from .services import get_diarios, set_favourite_course, set_visible_course

api = NinjaAPI(docs_decorator=staff_member_required)


@api.api_operation(["GET", "OPTIONS"], "/diarios/")
def diarios(
    request: HttpRequest,
    response: HttpResponse,
    semestre: str = None,
    situacao: str = None,
    ordenacao: str = None,
    disciplina: str = None,
    curso: str = None,
    ambiente: str = None,
    q: str = None,
    page: int = 1,
    page_size: int = 9,
):
    if request.method == "OPTIONS":
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    elif request.method == "GET":
        response["Access-Control-Allow-Origin"] = "*"
        return get_diarios(
            username=logged_user(request).username,
            semestre=semestre,
            situacao=situacao,
            disciplina=disciplina,
            curso=curso,
            ambiente=ambiente,
            q=q,
            page=page,
            page_size=page_size,
        )


@api.get("/atualizacoes_counts/")
def atualizacoes_counts(request: HttpRequest):
    # print("get_atualizacoes:",get_atualizacoes_counts(logged_user(request).username))
    # return get_atualizacoes_counts(logged_user(request).username)
    return {
        "atualizacoes": [],
        "unread_notification_total": 0,
        "unread_conversations_total": 0,
    }


@api.api_operation(["GET", "OPTIONS"], "/set_favourite/")
def set_favourite(request: HttpRequest, response: HttpResponse, ava: str, courseid: int, favourite: int):
    if request.method == "OPTIONS":
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    elif request.method == "GET":
        response["Access-Control-Allow-Origin"] = "*"
        return set_favourite_course(logged_user(request).username, ava, courseid, favourite)


@api.get("/set_visible/")
def set_visible(request: HttpRequest, ava: str, courseid: int, visible: int):
    return set_visible_course(logged_user(request).username, ava, courseid, visible)
