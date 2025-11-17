import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from a4.models import logged_user, Usuario
from painel.models import Ambiente, Situacao, Theme
from painel.services import get_json_api
import json


logger = logging.getLogger(__name__)


def __get_theme_prefix(request: HttpRequest) -> str:
    instance = Theme.objects.filter(nome=request.user.theme_selected, active=True).first()
    if instance is None:
        return "theme/ifrn25"

    return f"theme/{request.user.theme_selected}"


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, __get_theme_prefix(request) + "/frontpage/index.html")


@login_required
def change_theme(request: HttpRequest, theme: str) -> HttpResponse:
    instance = Theme.objects.filter(nome=theme, active=True).first()
    if instance is None:
        return redirect("painel:dashboard")

    user: Usuario = request.user
    if user.settings is None:
        user.settings = {}
    if "theme" not in user.settings:
        user.settings["theme"] = {}
    user.settings["theme"]["selected"] = theme
    user.save()
    return redirect("painel:dashboard")


@csrf_exempt
@login_required
def change_preference(request: HttpRequest, category: str, key: str) -> HttpResponse:
    if request.method == "POST":
        user: Usuario = request.user

        try:
            data = json.loads(request.body)
            value = data.get("value")

            if value == "true":
                parsed_value = True
            elif value == "false":
                parsed_value = False
            elif isinstance(value, bool):
                parsed_value = value
            else:
                parsed_value = value

            if user.settings is None:
                user.settings = {}

            if category not in user.settings:
                user.settings[category] = {}

            user.settings[category][key] = parsed_value
            user.save()

            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
@require_POST
def change_menu_position(request: HttpRequest) -> JsonResponse:
    position = request.POST.get("position")
    if position not in ("top", "bottom"):
        return JsonResponse({"error": "Valor inválido"}, status=400)

    user = request.user
    if user.settings is None:
        user.settings = {}
    user.settings["menu_position"] = position
    user.save(update_fields=["settings"])
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
