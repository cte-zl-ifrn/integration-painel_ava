import ast
import concurrent
import json
import logging
import re
import urllib.parse
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

CURSOS_CACHE = {}

CHANGE_URL = re.compile("/course/view.php\\?")


def _build_user_contexts(usuario_db) -> list:
    """
    Lê o 'last_json' e a lista de 'vinculos' para montar uma lista de contextos.
    """
    last_json = {}
    if usuario_db and usuario_db.last_json:
        try:
            last_json = json.loads(usuario_db.last_json)
        except Exception as e:
            logger.error(f"Erro {e}")

    vinculos_data = []
    if usuario_db and hasattr(usuario_db, "vinculos") and usuario_db.vinculos:
        v_raw = usuario_db.vinculos
        if isinstance(v_raw, str):
            try:
                v_raw = json.loads(v_raw)
            except Exception as e:
                logger.error(f"Erro {e}")
        if isinstance(v_raw, dict):
            vinculos_data = v_raw.get("results", [])
        elif isinstance(v_raw, list):
            vinculos_data = v_raw

    tipo_usuario_principal = str(last_json.get("tipo_usuario") or "").lower()
    campus_principal = str(last_json.get("campus") or "").lower()
    situacao_principal = str(last_json.get("situacao") or "").lower()

    contexts = []
    if not vinculos_data:
        vinculos_data = [{}]

    for v in vinculos_data:
        situacao_vinculo = str(v.get("situacao") or "").lower()
        if situacao_vinculo and situacao_vinculo not in ["ativo", "matriculado"]:
            continue

        detalhamento = v.get("detalhamento") or {}

        context = {
            "tipo_usuario": {tipo_usuario_principal, str(v.get("tipo") or "").lower()},
            "tipo": {str(v.get("tipo") or "").lower()},
            "campus": {campus_principal, str(v.get("campus") or "").lower()},
            "estrangeiro": {"true" if v.get("estrangeiro") else "false"},
            "situacao": {situacao_principal, situacao_vinculo},
            "detalhamento.modalidade": {str(detalhamento.get("modalidade") or "").lower()},
            "detalhamento.nivel_ensino": {str(detalhamento.get("nivel_ensino") or "").lower()},
            "detalhamento.curso": {str(detalhamento.get("curso") or "").lower()},
        }

        for key in context:
            context[key] = {val for val in context[key] if val}
        contexts.append(context)

    if not contexts:
        contexts.append(
            {"tipo_usuario": {tipo_usuario_principal}, "campus": {campus_principal}, "situacao": {situacao_principal}}
        )

    return contexts


def _parse_moodle_value(val_str: str) -> list:
    """Converte listas strings do Moodle (ex: "['A', 'B']") em listas Python em minúsculo."""
    val_str = val_str.strip()
    val_str_py = re.sub(r"\bfalse\b", "False", val_str)
    val_str_py = re.sub(r"\btrue\b", "True", val_str_py)

    try:
        parsed = ast.literal_eval(val_str_py)
        if isinstance(parsed, list):
            return [str(i).lower() for i in parsed]
        return [str(parsed).lower()]
    except ValueError, SyntaxError:
        return [v.strip().strip("'").strip('"').lower() for v in val_str.strip("[]").split(",") if v.strip()]


def _evaluate_simple_condition(context: dict, expr: str) -> bool:
    """Avalia uma condição unitária (ex: "m.campus in ['CNAT', 'ZL']") contra um vínculo único."""
    match = re.match(r"([\w\.]+)\s+(==|in)\s+(.*)", expr.strip())
    if not match:
        return False

    field, op, val_str = match.groups()
    if field.startswith("m."):
        field = field[2:]

    expected_values = set(_parse_moodle_value(val_str))
    user_values = context.get(field, set())

    return bool(user_values.intersection(expected_values))


def _evaluate_complex_rule(rule_str: str, user_contexts: list) -> bool:
    """Lê a expressão maior e cruza as lógicas AND e $any() com os contextos do usuário."""
    any_blocks = re.findall(r"\$any\(\[\s*(.*?)\s+for\s+m\s+in\s+outras_matriculas\s*\]\)", rule_str)

    rest_str = re.sub(r"\$any\(\[.*?\]\)", "", rule_str)
    simple_conditions = [c.strip() for c in rest_str.split(" and ") if c.strip()]

    # Devem passar em *pelo menos um* dos vínculos do usuário
    for cond in simple_conditions:
        passou_global = False
        for context in user_contexts:
            if _evaluate_simple_condition(context, cond):
                passou_global = True
                break
        if not passou_global:
            return False

    # Todo bloco interno verdadeiro para o *MESMO* vínculo
    for inner_rule in any_blocks:
        inner_conds = [c.strip() for c in inner_rule.split(" and ")]

        passou_neste_any = False
        for context in user_contexts:
            passou_todas_internas = True
            for ic in inner_conds:
                if not _evaluate_simple_condition(context, ic):
                    passou_todas_internas = False
                    break

            if passou_todas_internas:
                passou_neste_any = True
                break

        if not passou_neste_any:
            return False

    return True


def _filtrar_autoinscricoes_vitrine(autoinscricoes: list, username_logado: str) -> list:
    if not autoinscricoes:
        return []

    usuario_db = Usuario.objects.filter(username=username_logado).first()
    user_contexts = _build_user_contexts(usuario_db)

    cursos_vitrine_filtrados = []

    for curso_vitrine in autoinscricoes:
        restricoes_raw = curso_vitrine.get("restricoes_de_autoinscricao", "")

        regras = []
        if isinstance(restricoes_raw, str) and restricoes_raw.strip():
            if restricoes_raw.startswith("[") or restricoes_raw.startswith("{"):
                try:
                    parsed = json.loads(restricoes_raw)
                    if isinstance(parsed, list):
                        regras.extend([r["chave"] for r in parsed if isinstance(r, dict) and "chave" in r])
                    elif isinstance(parsed, dict) and "chave" in parsed:
                        regras.append(parsed["chave"])
                except json.JSONDecodeError:
                    logger.error(f"Erro ao ler JSON de restrições: {restricoes_raw}")
                    continue
            else:
                regras.append(restricoes_raw.strip())
        elif isinstance(restricoes_raw, list):
            for item in restricoes_raw:
                if isinstance(item, dict) and "chave" in item:
                    regras.append(item["chave"])
                elif isinstance(item, str):
                    regras.append(item)

        if not regras:
            continue

        passou_nos_filtros = False

        for regra_str in regras:
            if _evaluate_complex_rule(regra_str, user_contexts):
                passou_nos_filtros = True
                break

        if passou_nos_filtros:
            cursos_vitrine_filtrados.append(curso_vitrine)

    return cursos_vitrine_filtrados


def requests_get(url, headers={}, encoding="utf-8", decode=True, **kwargs):
    response = requests.get(url, headers=headers, timeout=2, **kwargs)
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
    except requests.exceptions.RequestException:
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

    def _get_diarios(params: Dict[str, Any]):
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
                curso_bd = next(iter(Curso.cached_by_codigos([co_curso])), None)
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

            # Filtragem de autoinscrições baseada no perfil do usuário
            username_logado = params.get("username", "")
            result["autoinscricoes"] = _filtrar_autoinscricoes_vitrine(
                result.get("autoinscricoes", []), username_logado
            )

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
        logger.debug("Results cache hit")
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
        "autoinscricoes": [],
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
            except Exception as e:
                logger.error(f"Erro ({e}) ao tentar cadastrar o curso {c}")

    results["cursos"] = [{"id": "", "label": "Cursos..."}] + deduplicate_and_sort(results["cursos"])

    for k in results.keys():
        if k not in CHAVES_ESTATICAS and isinstance(results[k], list):
            if len(results[k]) > 0 and isinstance(results[k][0], dict) and "fullname" in results[k][0]:
                results[k] = sorted(results[k], key=lambda e: e.get("fullname", ""))

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
        for x in ArquivoBackup.objects.filter(donoarquivobackup__dono_backup__username=username)
    ]

    cache.set(cache_key, results)
    logger.debug("Putting cache entry for get_diarios")

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
