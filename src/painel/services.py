import concurrent
import json
import logging
import re
import urllib.parse
from functools import lru_cache
from http.client import HTTPException
from typing import Any, Dict, List, Union

import requests
import sentry_sdk
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.urls import reverse

from a4.models import Usuario
from backup.models import ArquivoBackup

from .models import Ambiente, Curso

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

CODIGO_COORDENACAO_REGEX = re.compile(r"^(\w*)\.(\d+)(.*)?$")
CODIGO_COORDENACAO_ELEMENTS_COUNT = 3
CODIGO_COORDENACAO_CAMPUS_INDEX = 0
CODIGO_COORDENACAO_CURSO_INDEX = 1
CODIGO_COORDENACAO_SUFIXO_INDEX = 2

CODIGO_PRATICA_REGEX = re.compile("^(\\d\\d\\d\\d\\d)\\.(\\d*)\\.(\\d*)\\.(.*)\\.(\\d{11,14}\\d*)$")
CODIGO_PRATICA_ELEMENTS_COUNT = 5
CODIGO_PRATICA_SUFIXO_INDEX = 4

CHANGE_URL = re.compile("/course/view.php\\?")


def _filtrar_autoinscricoes(autoinscricoes: list, usuario_db: Usuario) -> list:
    if not autoinscricoes or not usuario_db:
        return []

    return [c for c in autoinscricoes if usuario_db.check_autoinscricao(c.get("restricoes_de_autoinscricao", ""))]


def requests_get(url, headers={}, encoding="utf-8", decode=True, **kwargs):
    response = requests.get(url, headers=headers, timeout=settings.DEFAULT_HTTP_TIMEOUT, **kwargs)
    byte_array_content = response.content
    content = byte_array_content.decode(encoding) if decode and encoding is not None else byte_array_content
    if response.ok:
        return content
    else:
        split_url = urllib.parse.urlsplit(url)
        safe_url = f"{split_url.scheme}://{split_url.netloc}{split_url.path}"
        logger.error(f"Error fetching {safe_url}: {response.status_code} - {response.reason}")
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
    except (requests.exceptions.RequestException, HTTPException) as e:
        logger.error(f"⚠️ TIMEOUT OU ERRO DE REDE no Moodle '{ava.nome}' ao acessar {url}: {e}")
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

    CHAVES_ESTATICAS = ["semestres", "disciplinas", "cursos", "ambientes", "autoinscricoes", "reutilizaveis"]

    @lru_cache(maxsize=1024)
    def get_curso_cached(co_curso):
        cache_key = f"curso:{co_curso}"
        curso_bd = cache.get(cache_key)
        if not curso_bd:
            curso_bd = Curso.objects.filter(codigo=co_curso).first()
            if curso_bd:
                cache.set(cache_key, curso_bd, timeout=86400)
        return curso_bd

    usuario_db = Usuario.cached(username)

    def _merge_course(diario: dict, ambiente: dict):
        # ========== 1. DADOS NOVOS (CUSTOM FIELDS) ==========
        co_curso = diario.get("curso_codigo")
        turma_nova = diario.get("turma_ano_periodo")
        componente_novo = diario.get("disciplina_sigla")
        id_diario_novo = diario.get("diario_id")

        # ========== 2. FALLBACK LEGADO (RegEx) ==========
        codigo = diario.get("shortname", "")
        diario_re = CODIGO_DIARIO_REGEX.findall(codigo)
        coordenacao_re = CODIGO_COORDENACAO_REGEX.findall(codigo)
        pratica_re = CODIGO_PRATICA_REGEX.findall(codigo)

        # --- CURSO ---
        if not co_curso:
            if diario_re and len(diario_re[0]) > CODIGO_DIARIO_CURSO_INDEX:
                co_curso = diario_re[0][CODIGO_DIARIO_CURSO_INDEX]
            elif pratica_re and len(pratica_re[0]) > CODIGO_DIARIO_CURSO_INDEX:
                co_curso = pratica_re[0][CODIGO_DIARIO_CURSO_INDEX]
            elif coordenacao_re and len(coordenacao_re[0]) > CODIGO_COORDENACAO_CURSO_INDEX:
                co_curso = coordenacao_re[0][CODIGO_COORDENACAO_CURSO_INDEX]

        if co_curso:
            curso_bd = get_curso_cached(co_curso)
            if curso_bd is not None:
                diario["curso"] = {"codigo": curso_bd.codigo, "nome": curso_bd.nome}
            else:
                diario["curso"] = {"codigo": co_curso, "nome": diario.get("curso_descricao") or f"Curso {co_curso}"}
        else:
            diario["curso"] = {"codigo": "", "nome": diario.get("curso_descricao") or "Curso Desconhecido"}

        # --- TURMA ---
        if turma_nova:
            diario["turma"] = turma_nova
        elif diario_re and len(diario_re[0]) > CODIGO_DIARIO_TURMA_INDEX:
            diario["turma"] = ".".join(diario_re[0][0 : CODIGO_DIARIO_TURMA_INDEX + 1])
        elif pratica_re and len(pratica_re[0]) > CODIGO_DIARIO_TURMA_INDEX:
            diario["turma"] = ".".join(pratica_re[0][0 : CODIGO_DIARIO_TURMA_INDEX + 1])

        # --- COMPONENTE ---
        if componente_novo:
            diario["componente"] = componente_novo
        elif diario_re and len(diario_re[0]) > CODIGO_DIARIO_DISCIPLINA_INDEX:
            diario["componente"] = diario_re[0][CODIGO_DIARIO_DISCIPLINA_INDEX]
        elif pratica_re and len(pratica_re[0]) > CODIGO_PRATICA_SUFIXO_INDEX:
            diario["componente"] = pratica_re[0][CODIGO_PRATICA_SUFIXO_INDEX]

        # --- ID DO DIÁRIO ---
        if id_diario_novo:
            diario["id_diario"] = str(id_diario_novo)
            diario["id_diario_clean"] = int(id_diario_novo) if str(id_diario_novo).isnumeric() else None
        elif diario_re and len(diario_re[0]) > CODIGO_DIARIO_ID_DIARIO_INDEX:
            id_diario_hash = diario_re[0][CODIGO_DIARIO_ID_DIARIO_INDEX]
            diario["id_diario"] = id_diario_hash
            diario["id_diario_clean"] = int(id_diario_hash[1:]) if id_diario_hash else None

        # ========== 3. URLs EXTRAS ==========
        def _merge_extra_urls(diario: dict, ava: dict):
            id_diario = diario.get("id_diario_clean", None)

            if diario.get("can_set_visibility") and id_diario:
                diario["can_check_grades"] = True
                diario["checkgradesurl"] = reverse(
                    "painel:checkgrades", kwargs={"id_ambiente": ava["ambiente"]["id"], "id_diario": id_diario}
                )
                diario["mensagemurl"] = f"{settings.OAUTH['BASE_URL']}/edu/enviar_mensagem/?diario={id_diario}"

            if id_diario:
                diario["suapsurl"] = f"{settings.OAUTH['BASE_URL']}/edu/meu_diario/{id_diario}/1/"
                if diario.get("can_set_visibility"):
                    diario["gradesurl"] = re.sub("/course/view", "/grade/report/grader/index", diario["viewurl"])
                else:
                    diario["gradesurl"] = re.sub("/course/view", "/grade/report/overview/index", diario["viewurl"])

        if diario.get("id_diario_clean"):
            _merge_extra_urls(diario, ambiente)

        return {**diario, **ambiente}

    def _get_diarios(params: Dict[str, Any]):
        logger.debug(f"Consultando API do Moodle para o ambiente {params['ambiente'].nome} com os parâmetros: {params}")

        try:
            ambiente = params["ambiente"]
            ambientedict = {
                "ambiente": {
                    "id": ambiente.id,
                    "titulo": ambiente.nome,
                    "cor_mestra": ambiente.cor_mestra,
                }
            }

            querystrings = {
                k: v for k, v in params.items() if k not in ["ambiente", "results"] and str(v).strip() != ""
            }

            if "q" in querystrings:
                querystrings["q"] = urllib.parse.quote(querystrings["q"])

            result = get_json_api(ambiente, "get_diarios", **querystrings) or {}

            # Filtragem de autoinscrições baseada no perfil do usuário
            usuario_db_param = params.get("usuario_db")
            result["autoinscricoes"] = _filtrar_autoinscricoes(result.get("autoinscricoes", []), usuario_db_param)

            for k, v in result.items():
                # 1. Se a chave for nova (ex: 'projetos'), cria a lista vazia no dicionário global
                if k not in params["results"]:
                    params["results"][k] = []

                # 2. Tratamento específico para autoinscrições (vitrine)
                if k == "autoinscricoes":

                    def _merge_vitrine(curso_vitrine: dict, amb_dict: dict):
                        ambiente_id = amb_dict["ambiente"]["id"]
                        curso_id = curso_vitrine["id"]

                        curso_vitrine["details_url"] = reverse(
                            "painel:curso_detalhes", kwargs={"id_ambiente": ambiente_id, "id_curso": curso_id}
                        )
                        return {**curso_vitrine, **amb_dict}

                    params["results"][k] += [_merge_vitrine(c, ambientedict) for c in v or []]

                # 3. Tratamento para filtros (não precisam de merge de curso)
                elif k in CHAVES_ESTATICAS:
                    params["results"][k] += v or []

                # 4. Tratamento DINÂMICO para todas as salas (diarios, praticas, nova_sala...)
                else:
                    params["results"][k] += [_merge_course(diario, ambientedict) for diario in v or []]

        except Exception as e:
            logging.error(e)
            sentry_sdk.capture_exception(e)

    def deduplicate_and_sort(list_of_dict: Union[None, List[Dict[str, str]]], reverse: bool = False):
        deduplicated = [{"id": x, "label": y} for x, y in ({x["id"]: x["label"] for x in list_of_dict}).items()]
        sortedlist = sorted(deduplicated, key=lambda e: e["label"], reverse=reverse)
        return sortedlist

    has_ambiente = ambiente != "" and ambiente is not None and f"{ambiente}".isnumeric()
    ambientes = [ava for ava in Ambiente.cached() if (has_ambiente and int(ambiente) == ava.id) or not has_ambiente]
    logger.debug(f"Ambientes selecionados para consulta: {[a.moodle_base_api_url for a in ambientes]}")

    results = {
        "semestres": [],
        "ambientes": Ambiente.as_dict(),
        "disciplinas": [],
        "cursos": [],
        "diarios": [],
        "coordenacoes": [],
        "praticas": [],
        "reutilizaveis": [],
        "autoinscricoes": [],
    }

    requests = [
        {
            "ambiente": ava,
            "username": username.lower(),
            "usuario_db": usuario_db,
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
    cursos = {}
    for cod in codigos:
        curso_bd = get_curso_cached(cod)
        if curso_bd:
            cursos[cod] = curso_bd.nome

    cursos_a_criar = []
    for c in results["cursos"]:
        if c["id"] in cursos:
            c["label"] = f"{cursos[c['id']]}"
        else:
            c["label"] = f"Curso [{c['id']}], favor solicitar o cadastro"
            cursos_a_criar.append(Curso(codigo=c["id"], nome=f"Curso [{c['id']}], favor solicitar o cadastro"))

    if cursos_a_criar:
        try:
            Curso.objects.bulk_create(cursos_a_criar, ignore_conflicts=True)
            cache.delete("cursos")
        except Exception as e:
            logger.error(f"Erro ao tentar cadastrar cursos em lote: {e}")

    results["cursos"] = [{"id": "", "label": "Cursos..."}] + deduplicate_and_sort(results["cursos"])

    def course_sort_key(e):
        ano_periodo_str = str(e.get("turma_ano_periodo") or "")
        ano_periodo = 0

        match = re.search(r"(\d{4})\.?(\d)", ano_periodo_str)
        if match:
            ano_periodo = int(match.group(1) + match.group(2))
        else:
            match = re.search(r"(\d{4})", ano_periodo_str)
            if match:
                ano_periodo = int(match.group(1) + "0")

        return (-ano_periodo, (e.get("fullname") or "").lower())

    for k in results.keys():
        if k not in CHAVES_ESTATICAS and isinstance(results[k], list):
            if len(results[k]) > 0 and isinstance(results[k][0], dict) and "fullname" in results[k][0]:
                results[k] = sorted(results[k], key=course_sort_key)

    results["reutilizaveis"] = [
        {
            "id": x.id,
            "shortname": x.nome_arquivo,
            "fullname": x.curso_nome,
            "url": x.url_sem_dados,
            "donos": [
                {
                    "username": d.dono_backup.username,
                    "fullname": d.dono_backup.nome,
                }
                for d in x.donoarquivobackup_set.all()
            ],
        }
        for x in ArquivoBackup.objects.filter(donoarquivobackup__dono_backup__username=username).prefetch_related(
            "donoarquivobackup_set__dono_backup"
        )
    ]

    return results


def set_favourite_course(username: str, ava: str, courseid: int, favourite: int) -> dict:
    ava = get_object_or_404(Ambiente, nome=ava)

    return (
        get_json_api(ava, "set_favourite_course", username=username.lower(), courseid=courseid, favourite=favourite)
        or {}
    )


def set_visible_course(username: str, ava: str, courseid: int, visible: int) -> dict:
    ava = get_object_or_404(Ambiente, nome=ava)

    return get_json_api(ava, "set_visible_course", username=username.lower(), courseid=courseid, visible=visible) or {}


def set_user_preference(username: str, ava: str, name: str, value: str) -> dict:
    ava = get_object_or_404(Ambiente, nome=ava)

    return get_json_api(ava, "set_user_preference", username=username.lower(), name=name, value=value) or {}


def get_progresso(username: str, ambiente: str = None, cursos: str = None) -> dict:
    import threading

    lock = threading.Lock()

    has_ambiente = ambiente != "" and ambiente is not None and f"{ambiente}".isnumeric()
    ambientes = [ava for ava in Ambiente.cached() if (has_ambiente and int(ambiente) == ava.id) or not has_ambiente]

    results = []

    def _get_progresso_moodle(params: dict):
        ava = params["ambiente"]
        querystrings = {"username": params["username"]}
        if params.get("cursos"):
            querystrings["cursos"] = params["cursos"]

        try:
            data = get_json_api(ava, "get_progresso", **querystrings) or []
            if data:
                for item in data:
                    item["ambiente_id"] = ava.id

                with lock:
                    params["results"].extend(data)
        except Exception as e:
            logger.error(f"Erro em get_progresso ({ava.nome}): {e}")

    requests_args = [
        {
            "ambiente": ava,
            "username": username.lower(),
            "cursos": cursos,
            "results": results,
        }
        for ava in ambientes
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(_get_progresso_moodle, requests_args)

    return {"progresso": results}
