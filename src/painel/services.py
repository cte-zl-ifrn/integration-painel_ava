import logging
import concurrent
import re
import json
import urllib.parse
import sentry_sdk
from typing import Dict, List, Union, Any
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
import requests
from http.client import HTTPException
from .models import Ambiente, Curso
from backup.models import ArquivoBackup


logger = logging.getLogger(__name__)


CODIGO_DIARIO_REGEX = re.compile("^(\\d\\d\\d\\d\\d)\\.(\\d*)\\.(\\d*)\\.(.*)\\.(\\w*\\.\\d*)(#\\d*)?$")
CODIGO_DIARIO_ANTIGO_ELEMENTS_COUNT = 5
CODIGO_DIARIO_NOVO_ELEMENTS_COUNT = 6
CODIGO_DIARIO_SEMESTRE_INDEX = 0
CODIGO_DIARIO_PERIODO_INDEX = 1
CODIGO_DIARIO_CURSO_INDEX = 2
CODIGO_DIARIO_TURMA_INDEX = 3
CODIGO_DIARIO_DISCIPLINA_INDEX = 4
CODIGO_DIARIO_ID_DIARIO_INDEX = 5

CODIGO_COORDENACAO_REGEX = re.compile("^(\\w*)\\.(\\d*)(.*)*$")
CODIGO_COORDENACAO_ELEMENTS_COUNT = 3
CODIGO_COORDENACAO_CAMPUS_INDEX = 0
CODIGO_COORDENACAO_CURSO_INDEX = 1
CODIGO_COORDENACAO_SUFIXO_INDEX = 2

CODIGO_PRATICA_REGEX = re.compile("^(\\d\\d\\d\\d\\d)\\.(\\d*)\\.(\\d*)\\.(.*)\\.(\\d{11,14}\\d*)$")
CODIGO_PRATICA_ELEMENTS_COUNT = 5
CODIGO_PRATICA_SUFIXO_INDEX = 4

CURSOS_CACHE = {}

CHANGE_URL = re.compile("/course/view.php\\?")


def requests_get(url, headers={}, encoding="utf-8", decode=True, **kwargs):
    response = requests.get(url, headers=headers, **kwargs)
    byte_array_content = response.content
    content = byte_array_content.decode(encoding) if decode and encoding is not None else byte_array_content
    if response.ok:
        return content
    else:
        logger.error(f"Error fetching {url}: {response.status_code} - {response.reason}\n{content}")
        exc = HTTPException("%s - %s" % (response.status_code, response.reason))
        exc.status = response.status_code
        exc.reason = response.reason
        exc.headers = response.headers
        exc.url = url
        raise exc


def get_json(url, headers={}, encoding="utf-8", json_kwargs=None, **kwargs):
    content = requests_get(url, headers=headers, encoding=encoding, **kwargs)
    return json.loads(content, **(json_kwargs or {}))


def get_json_api(ava: Ambiente, service: str, **params: dict):
    if params is not None:
        querystring = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
    else:
        querystring = ""
    url = f"{ava.moodle_base_api_url}/?{service}&{querystring}"
    try:
        return get_json(url, headers={"Authentication": f"Token {ava.token}"})
    except requests.exceptions.RequestException as e:
        return None


def get_diarios(
    username: str,
    semestre: str = None,
    situacao: str = None,
    disciplina: str = None,
    curso: str = None,
    ambiente: str = None,
    q: str = None,
    page: int = 1,
    page_size: int = 21,
) -> dict:
    def _get_diarios(params: Dict[str, Any]):
        def _merge_course(diario: dict, ambiente: dict):
            def _merge_curso(diario: dict, diario_re: re.Match):
                if not diario_re and len(diario_re[0]) not in (
                    CODIGO_DIARIO_ANTIGO_ELEMENTS_COUNT,
                    CODIGO_DIARIO_NOVO_ELEMENTS_COUNT,
                    CODIGO_COORDENACAO_ELEMENTS_COUNT,
                    CODIGO_PRATICA_ELEMENTS_COUNT,
                ):
                    return

                if len(diario_re[0]) == CODIGO_COORDENACAO_ELEMENTS_COUNT:
                    co_curso = diario_re[0][CODIGO_COORDENACAO_CURSO_INDEX]
                else:
                    co_curso = diario_re[0][CODIGO_DIARIO_CURSO_INDEX]
                curso = next(iter(Curso.cached_by_codigos([co_curso])), None)
                if curso is not None:
                    diario["curso"] = {"codigo": curso.codigo, "nome": curso.nome}
                else:
                    diario["curso"] = {"codigo": co_curso, "nome": f"Curso {co_curso}"}

            def _merge_turma(diario: dict, diario_re: re.Match):
                if len(diario_re) > 0 and len(diario_re[0]) >= CODIGO_DIARIO_TURMA_INDEX:
                    diario["turma"] = ".".join(diario_re[0][0 : CODIGO_DIARIO_TURMA_INDEX + 1])

            def _merge_componente(diario: dict, diario_re: re.Match):
                if len(diario_re) > 0 and len(diario_re[0]) >= CODIGO_DIARIO_DISCIPLINA_INDEX:
                    diario["componente"] = diario_re[0][CODIGO_DIARIO_DISCIPLINA_INDEX]

            def _merge_id_diario(diario: dict, diario_re: re.Match):
                if len(diario_re) > 0 and len(diario_re[0]) >= CODIGO_DIARIO_ID_DIARIO_INDEX:
                    id_diario_hash = diario_re[0][CODIGO_DIARIO_ID_DIARIO_INDEX]
                    diario["id_diario"] = id_diario_hash
                    diario["id_diario_clean"] = int(id_diario_hash[1:]) if id_diario_hash else None

            def _merge_extra_urls(diario: dict, ava: Ambiente):
                id_diario = diario.get("id_diario_clean", None)

                if diario.get("can_set_visibility") and id_diario:
                    diario["can_check_grades"] = True
                    diario["checkgradesurl"] = reverse(
                        "painel:checkgrades", kwargs={"id_ambiente": ava["ambiente"]["id"], "id_diario": id_diario}
                    )

                    diario["mensagemurl"] = f"{settings.OAUTH["BASE_URL"]}/edu/enviar_mensagem/?diario={id_diario}"

                if id_diario:
                    diario["suapsurl"] = f"{settings.OAUTH["BASE_URL"]}/edu/meu_diario/{id_diario}/1/"
                    if diario.get("can_set_visibility"):
                        diario["gradesurl"] = re.sub("/course/view", "/grade/report/grader/index", diario["viewurl"])
                    else:
                        diario["gradesurl"] = re.sub("/course/view", "/grade/report/overview/index", diario["viewurl"])

            def _merge_aluno(diario: dict, diario_re: re.Match):
                if diario_re and len(diario_re[0]) > CODIGO_PRATICA_SUFIXO_INDEX:
                    diario["componente"] = diario_re[0][CODIGO_PRATICA_SUFIXO_INDEX]

            codigo = diario["shortname"]
            diario_re = CODIGO_DIARIO_REGEX.findall(codigo)
            coordenacao_re = CODIGO_COORDENACAO_REGEX.findall(codigo)
            pratica_re = CODIGO_PRATICA_REGEX.findall(codigo)

            if diario_re:
                _merge_curso(diario, diario_re)
                _merge_turma(diario, diario_re)
                _merge_componente(diario, diario_re)
                _merge_id_diario(diario, diario_re)
                _merge_extra_urls(diario, ambiente)
            elif pratica_re:
                _merge_curso(diario, pratica_re)
                _merge_turma(diario, pratica_re)
                _merge_aluno(diario, pratica_re)
            elif coordenacao_re:
                _merge_curso(diario, coordenacao_re)
            return {**diario, **ambiente}

        try:
            ambiente = params["ambiente"]
            ambientedict = {
                "ambiente": {
                    "id": ambiente.id,
                    "titulo": ambiente.nome,
                    "cor_mestra": ambiente.cor_mestra,
                }
            }

            querystrings = {k: v for k, v in params.items() if k not in ["ambiente", "results"]}

            if "q" in querystrings:
                querystrings["q"] = urllib.parse.quote(querystrings["q"])

            result = get_json_api(ambiente, "get_diarios", **querystrings) or {}

            for k, v in params["results"].items():
                if k in result:
                    if k in ["diarios", "coordenacoes", "praticas"]:
                        params["results"][k] += [_merge_course(diario, ambientedict) for diario in result[k] or []]
                    else:
                        params["results"][k] += result[k] or []

        except Exception as e:
            logging.error(e)
            sentry_sdk.capture_exception(e)

    def deduplicate_and_sort(list_of_dict: Union[None, List[Dict[str, str]]], reverse: bool = False):
        deduplicated = [{"id": x, "label": y} for x, y in ({x["id"]: x["label"] for x in list_of_dict}).items()]
        sortedlist = sorted(deduplicated, key=lambda e: e["label"], reverse=reverse)
        return sortedlist

    if not cache.get("keys"):
        cache.set("keys", [])

    cache_key = (
        f"get_diarios:{username.lower()}:{semestre}:{situacao}:{disciplina}:{curso}:{ambiente}:{q}:{page}:{page_size}"
    )

    if cache_key not in cache.get("keys"):
        keys_list = cache.get("keys")
        keys_list.append(cache_key)
        cache.set("keys", keys_list)

    results = cache.get(cache_key, None)
    if results is not None:
        logger.debug(f"Results cache hit: {cache_key}")
        return results

    results = {
        "semestres": [],
        "ambientes": Ambiente.as_dict(),
        "disciplinas": [],
        "cursos": [],
        "diarios": [],
        "coordenacoes": [],
        "praticas": [],
        "reutilizaveis": [],
    }

    has_ambiente = ambiente != "" and ambiente is not None and f"{ambiente}".isnumeric()

    ambientes = [ava for ava in Ambiente.cached() if (has_ambiente and int(ambiente) == ava.id) or not has_ambiente]

    requests = [
        {
            "ambiente": ava,
            "username": username.lower(),
            "semestre": semestre,
            "situacao": situacao,
            "disciplina": disciplina,
            "curso": curso,
            "q": q,
            "page": page,
            "page_size": page_size,
            "results": results,
        }
        for ava in ambientes
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(_get_diarios, requests)

    results["semestres"] = [{"id": "", "label": "Semestres... "}] + deduplicate_and_sort(
        results["semestres"], reverse=True
    )
    results["disciplinas"] = [{"id": "", "label": "Disciplinas..."}] + deduplicate_and_sort(results["disciplinas"])
    results["ambientes"] = [
        {
            "label": "Ambientes...",
            "id": "",
            "color": None,
        }
    ] + sorted(results["ambientes"], key=lambda e: e["label"])

    codigos = [x["id"] for x in results["cursos"]]
    cursos = {c.codigo: c.nome for c in Curso.cached_by_codigos(codigos)}
    for c in results["cursos"]:
        if c["id"] in cursos:
            c["label"] = f"{cursos[c['id']]}"
        else:
            c["label"] = f"Curso [{c['id']}], favor solicitar o cadastro"
            try:
                curso = Curso()
                curso.codigo = c["id"]
                curso.nome = f"Curso [{c['id']}], favor solicitar o cadastro"
                curso.save()
            except:
                pass

    results["cursos"] = [{"id": "", "label": "Cursos..."}] + deduplicate_and_sort(results["cursos"])
    results["praticas"] = sorted(results["praticas"], key=lambda e: e["fullname"])
    results["coordenacoes"] = sorted(results["coordenacoes"], key=lambda e: e["fullname"])
    results["reutilizaveis"] = [
        {
            'id': x.id,
            'shortname': x.nome_arquivo,
            'fullname': x.curso_nome,
            'url': x.url_sem_dados,
            'donos': [
                {
                    'username': d.dono_backup.username,
                    'fullname': d.dono_backup.nome,
                } 
                for d in x.donoarquivobackup_set.all()
            ],
        }
        for x in ArquivoBackup.objects.filter(donoarquivobackup__dono_backup__username=username)
    ]

    cache.set(cache_key, results)
    logger.debug(f"Putting cache for: {cache_key}")

    return results


def set_favourite_course(username: str, ava: str, courseid: int, favourite: int) -> dict:
    ava = get_object_or_404(Ambiente, nome=ava)

    for v in cache.get("keys"):
        cache.delete(v)

    return (
        get_json_api(ava, "set_favourite_course", username=username.lower(), courseid=courseid, favourite=favourite)
        or {}
    )


def set_visible_course(username: str, ava: str, courseid: int, visible: int) -> dict:
    ava = get_object_or_404(Ambiente, nome=ava)

    keys = cache.get("keys") or []

    for v in keys:
        cache.delete(v)
        
    return get_json_api(ava, "set_visible_course", username=username.lower(), courseid=courseid, visible=visible) or {}


def set_user_preference(username: str, ava: str, name: str, value: str) -> dict:
    ava = get_object_or_404(Ambiente, nome=ava)

    keys = cache.get("keys") or []

    for v in keys:
        cache.delete(v)
        
    return get_json_api(ava, "set_user_preference", username=username.lower(), name=name, value=value) or {}