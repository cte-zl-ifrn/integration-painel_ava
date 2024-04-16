from ninja import NinjaAPI
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from a4.models import logged_user
from .services import get_diarios, get_atualizacoes_counts, set_favourite_course, set_visible_course


api = NinjaAPI(docs_decorator=staff_member_required)


@api.get("/diarios/")
def diarios(
    request: HttpRequest,
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
    return get_atualizacoes_counts(logged_user(request).username)


@api.get("/set_favourite/")
def set_favourite(request: HttpRequest, ava: str, courseid: int, favourite: int):
    return set_favourite_course(logged_user(request).username, ava, courseid, favourite)


@api.get("/set_visible/")
def set_visible(request: HttpRequest, ava: str, courseid: int, visible: int):
    return set_visible_course(logged_user(request).username, ava, courseid, visible)
