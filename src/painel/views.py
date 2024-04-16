from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from a4.models import logged_user
from painel.models import Ambiente, Situacao
from painel.services import get_json_api


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    # https://ead.ifrn.edu.br/ava/academico/lib/ajax/service.php?info=core_course_get_enrolled_courses_by_timeline_classification
    return render(request, "painel/dashboard/index.html")


# @login_required
# def syncs(request: HttpRequest, id_diario: int) -> HttpResponse:
#     solicitacoes = Solicitacao.objects.by_diario_id(id_diario)
#     return render(request, "painel/diario/syncs.html", context={"solicitacoes": solicitacoes})


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
    return render(
        request, "painel/diario/checkgrades.html", context={"diario": diario, "alunos": alunos, "etapas": etapas.keys()}
    )
