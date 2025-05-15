import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from a4.models import logged_user, Usuario
from painel.models import Ambiente, Situacao, Theme
from painel.services import get_json_api


logger = logging.getLogger(__name__)


def __get_theme_prefix(request: HttpRequest) -> str:
    user: Usuario = request.user
    selected = "ifrn25"
    if user.settings is not None and "theme" in user.settings and "selected" in user.settings["theme"]:
        selected = user.settings["theme"]["selected"]

    instance = Theme.objects.filter(nome=selected, active=True).first()
    logger.info(f"Theme {selected} does not exist")
    if instance is None:
        return "theme/ifrn25"

    return f"theme/{selected}"


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, __get_theme_prefix(request) + "/frontpage/index.html")


@login_required
def change_theme(request: HttpRequest, theme: str) -> HttpResponse:
    instance = Theme.objects.filter(nome=theme, active=True).first()
    if instance is None:
        return redirect("painel:dashboard")

    user: Usuario = request.user
    if user.settings is not None:
        user.settings = {}
    if "theme" not in user.settings:
        user.settings["theme"] = {}
    user.settings["theme"]["selected"] = theme
    user.save()
    return redirect("painel:dashboard")


@login_required
def checkgrades(request: HttpRequest, id_ambiente: int, id_diario: int) -> HttpResponse:
    ambiente = get_object_or_404(Ambiente, pk=id_ambiente)
    resposta = get_json_api(
        ambiente,
        "get_diarios",
        **{"username": logged_user(request).username, "q": f"%23{id_diario}", "situacao": Situacao.ALL},
    )
    diario = resposta["diarios"][0] if len(resposta.get("diarios", [])) == 1 else None
    if diario is None:
        raise Exception("Diário não encontrado")
    parts = diario.get("idnumber", "").split("#")
    diario["id_diario"] = parts[1] if len(parts) == 2 else None
    alunos = get_json_api(ambiente, "sync_down_grades", **{"diario_id": id_diario})
    etapas = {}
    for grade in alunos:
        if grade["notas"]:
            for nota in grade["notas"].keys():
                etapas[nota] = nota
    context = {"diario": diario, "alunos": alunos, "etapas": etapas.keys()}
    return render(request, __get_theme_prefix(request) + "/diario/checkgrades.html", context=context)
