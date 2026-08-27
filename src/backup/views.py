import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from painel.context_processors import logged_user
from painel.models import Ambiente, Situacao, Theme
from painel.v1.services import get_json_api

logger = logging.getLogger(__name__)


def get_user_profile(user):
    profile = getattr(user, "suap_profile", None)
    return profile if profile is not None else user


def __get_theme_prefix(request: HttpRequest) -> str:
    profile = get_user_profile(request.user)
    theme_selected = getattr(profile, "theme_selected", "ifrn25")
    instance = Theme.objects.filter(nome=theme_selected, active=True).first()
    if instance is None:
        return "theme/ifrn25"

    return f"theme/{theme_selected}"


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, __get_theme_prefix(request) + "/frontpage/index.html")


@login_required
def change_theme(request: HttpRequest, theme: str) -> HttpResponse:
    instance = Theme.objects.filter(nome=theme, active=True).first()
    if instance is None:
        return redirect("painel:dashboard")

    profile = get_user_profile(request.user)
    if profile.settings is None:
        profile.settings = {}
    if "theme" not in profile.settings:
        profile.settings["theme"] = {}
    profile.settings["theme"]["selected"] = theme
    profile.save()
    return redirect("painel:dashboard")


@login_required
@require_POST
def change_menu_position(request: HttpRequest) -> JsonResponse:
    position = request.POST.get("position")
    if position not in ("top", "bottom"):
        return JsonResponse({"error": "Valor inválido"}, status=400)

    profile = get_user_profile(request.user)
    if profile.settings is None:
        profile.settings = {}
    profile.settings["menu_position"] = position
    profile.save()
    return JsonResponse({"status": "ok", "position": position})


@login_required
def checkgrades(request: HttpRequest, id_ambiente: int, id_diario: int) -> HttpResponse:
    ambiente = get_object_or_404(Ambiente, pk=id_ambiente)
    resposta = (
        get_json_api(
            ambiente,
            "get_diarios",
            **{"username": logged_user(request).username, "q": f"%23{id_diario}", "situacao": Situacao.ALL},
        )
        or {}
    )
    diario = resposta["diarios"][0] if len(resposta.get("diarios", [])) == 1 else None
    if diario is None:
        raise Exception("Diário não encontrado")
    parts = diario.get("idnumber", "").split("#")
    diario["id_diario"] = parts[1] if len(parts) == 2 else None
    alunos = get_json_api(ambiente, "sync_down_grades", **{"diario_id": id_diario}) or []
    etapas = {}
    for grade in alunos:
        if grade["notas"]:
            for nota in grade["notas"].keys():
                etapas[nota] = nota
    context = {"diario": diario, "alunos": alunos, "etapas": etapas.keys()}
    return render(request, __get_theme_prefix(request) + "/diario/checkgrades.html", context=context)


@login_required
def completed_tour(request: HttpRequest) -> HttpResponse:
    profile = get_user_profile(request.user)
    if profile.settings is None:
        profile.settings = {}
    if "tour" not in profile.settings:
        profile.settings["tour"] = {}
    profile.settings["tour"]["completed"] = True
    profile.save()
    return JsonResponse({"status": "ok"})


@login_required
def get_tour_status(request: HttpRequest) -> HttpResponse:
    profile = get_user_profile(request.user)

    if profile.settings and "tour" in profile.settings and "completed" in profile.settings["tour"]:
        completed = profile.settings["tour"]["completed"]
    else:
        completed = False

    return JsonResponse({"completed_tour": completed})
