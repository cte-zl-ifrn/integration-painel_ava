import json
import logging
import re
import urllib

import requests
import sentry_sdk
from django.conf import settings
from django.contrib import auth
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.utils.timezone import now

from a4.models import Usuario

logger = logging.getLogger(__name__)


def _post(*args, **kwargs) -> requests.Response:
    return requests.post(*args, verify=settings.OAUTH["VERIFY_SSL"], timeout=2, **kwargs)


def _get(*args, **kwargs) -> requests.Response:
    return requests.get(*args, verify=settings.OAUTH["VERIFY_SSL"], timeout=2, **kwargs)


def login(request: HttpRequest) -> HttpResponse:
    o = settings.OAUTH
    suap_url = f"{o["AUTHORIZE_URL"]}?response_type=code&client_id={o["CLIENT_ID"]}&redirect_uri={o['REDIRECT_URI']}"
    return redirect(suap_url)


def logout(request: HttpRequest) -> HttpResponse:
    if request.user is not None and request.user.username is not None:
        cache.delete(f"username:{request.user.username}")
    auth.logout(request)

    logout_token = request.session.get("logout_token", "")
    next = urllib.parse.quote_plus(settings.LOGIN_REDIRECT_URL)
    return redirect(f"{settings.LOGOUT_REDIRECT_URL}?token={logout_token}&next={next}")


def authenticate(request: HttpRequest) -> HttpResponse:
    OAUTH = settings.OAUTH

    def oauth_error(error) -> HttpResponse:
        return render(request, "a4/oauth_error.html", {"error": error})

    def validate_request() -> None or HttpResponse:
        if "error" in request.GET:
            if request.GET["error"] == "access_denied":
                return render(request, "a4/not_authorized.html")
            else:
                return render(request, "a4/not_authorized.html")

        if "code" not in request.GET:
            return oauth_error("")

    def check_access_token() -> dict or HttpResponse:
        response_text = None
        try:
            reqeuest_data = {
                "grant_type": "authorization_code",
                "code": request.GET["code"],
                "redirect_uri": OAUTH["REDIRECT_URI"],
                "client_id": OAUTH["CLIENT_ID"],
                "client_secret": OAUTH["CLIENT_SECRET"],
            }
            logger.debug(f"access_token_request_data: {reqeuest_data}")

            response = _post(f"{OAUTH['TOKEN_URL']}", reqeuest_data)
            response_text = response.text
            logger.debug(f"access_token_response_text: {response_text}")

            if "invalid_grant" in response_text:
                return render(request, "a4/oauth_error_invalid_grant.html")

            if response.status_code != 200:
                sentry_sdk.capture_message(response_text)
                return oauth_error(response_text)

            data = json.loads(response_text)
            logger.debug(f"access_token_data: {data}")
            if data.get("error_description") == "Mismatching redirect URI.":
                sentry_sdk.capture_message(response_text)
                return oauth_error(str(data))

            return data
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return oauth_error(f"{e}. {response_text}")

    def get_user_info(access_token) -> dict or HttpResponse:
        response_text = None
        try:
            headers = {
                "Authorization": f"Bearer {access_token.get('access_token')}",
                "x-api-key": OAUTH["CLIENT_SECRET"],
            }
            safe_headers = {
                "Authorization": "[REDACTED]",
                "x-api-key": "[REDACTED]",
            }
            logger.debug(f"user_info_request_header: {safe_headers}")

            scope = access_token.get("scope", "identificacao email documentos_pessoais")
            response = _get(f"{OAUTH['USERINFO_URL']}?scope={scope}", headers=headers)
            response_text = response.text
            logger.debug(f"user_info_response_text: {response_text}")

            data = json.loads(response_text)
            logger.debug(f"user_info_data: {data}")

            if data.get("identificacao", None) is None:
                return oauth_error(f"O JSON retornado pelo SUAP não veio correto. {response_text}")

            return data
        except Exception as e:
            sentry_sdk.capture_exception(e)
            if response_text is not None and "__buscar_menu__" in response_text:
                vinculo_regex = re.compile(
                    '<span title=\\"Vínculo: (\\d*)\\">(\\w* \\w*)</span></a><a href="/comum/minha_conta/"'
                )
                parts = vinculo_regex.findall(response_text)[0]
                return render(
                    request,
                    "a4/oauth_usuario_sem_vinculo.html",
                    context={
                        "username": parts[0] if len(parts) > 0 else "[SEU CPF]",
                        "common_name": parts[1] if len(parts) > 0 else "[SEU NOME COMPLETO]",
                        "tem_foto": static("/comum/img/default.jpg") in response_text,
                    },
                )
            return oauth_error(f"{e}. {response_text}")

    def get_user_vinculos(access_token) -> tuple:
        dados_vinculos = None
        erro_vinculo = None
        try:
            headers = {
                "Authorization": f"Bearer {access_token.get('access_token')}",
                "x-api-key": OAUTH["CLIENT_SECRET"],
            }
            response = _get(OAUTH["VINCULOS_URL"], headers=headers)

            if response.status_code == 200:
                dados_vinculos = response.json()
            else:
                erro_vinculo = f"Erro API Vínculos (Status {response.status_code}): {response.text}"
                logger.warning(erro_vinculo)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            erro_vinculo = f"Exceção ao buscar vínculos: {str(e)}"

        return dados_vinculos, erro_vinculo

    def save_user(user_info, vinculos_data, erro_vinculo) -> Usuario or HttpResponse:
        try:
            username = user_info.get("identificacao", None)
            defaults = {
                "nome_registro": user_info.get("nome_registro"),
                "nome_social": user_info.get("nome_social"),
                "nome_usual": user_info.get("nome_usual"),
                "nome": user_info.get("nome"),
                "first_name": user_info.get("primeiro_nome"),
                "last_name": user_info.get("ultimo_nome"),
                "email": user_info.get("email_preferencial"),
                "email_corporativo": user_info.get("email"),
                "email_google_classroom": user_info.get("email_google_classroom"),
                "email_academico": user_info.get("email_academico"),
                "email_secundario": user_info.get("email_secundario"),
                "foto": user_info.get("foto"),
                "tipo_usuario": user_info.get("tipo_usuario"),
                "last_json": json.dumps(user_info),
                "vinculos": vinculos_data,
                "observacao_erro_vinculo": erro_vinculo,
            }

            user = Usuario.objects.filter(username=username).first()
            logger.debug(f"checking user: {user}")
            if user is None:
                is_superuser = Usuario.objects.count() == 0
                logger.debug("need to create user")
                user = Usuario.objects.create(
                    username=username,
                    is_superuser=is_superuser,
                    is_staff=is_superuser,
                    first_login=now(),
                    **defaults,
                )
            else:
                logger.debug(f"need to update user: {user}")
                if user.first_login is None:
                    user.first_login = now()
                    user.save()
                Usuario.objects.filter(username=username).update(**defaults)
            return user
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return oauth_error(f"{e}")

    result = validate_request()
    if isinstance(result, HttpResponse):
        return result

    access_token_data = check_access_token()
    if isinstance(access_token_data, HttpResponse):
        return access_token_data

    user_info_data = get_user_info(access_token_data)
    if isinstance(user_info_data, HttpResponse):
        return user_info_data

    vinculos_data, erro_vinculo = get_user_vinculos(access_token_data)

    user_model = save_user(user_info_data, vinculos_data, erro_vinculo)
    if isinstance(user_model, HttpResponse):
        return user_model

    auth.login(request, user_model)

    return redirect("painel:dashboard")


def personificar(request: HttpRequest, username: str):
    if not request.user.is_superuser:
        raise ValidationError("Só super usuários podem personificar")
    if "usuario_personificado" in request.session:
        raise ValidationError("Você já está personificando um usuário")

    u = get_object_or_404(Usuario, username=username)
    if u.is_superuser:
        raise ValidationError("Ninguém pode personificar um super usuário")

    request.session["usuario_personificado"] = username
    return redirect("painel:dashboard")


def despersonificar(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        raise ValidationError("Você não é um super usuário.")
    if "usuario_personificado" not in request.session:
        raise ValidationError("Você não está personificando um usuário.")
    del request.session["usuario_personificado"]
    return redirect("painel:dashboard")
