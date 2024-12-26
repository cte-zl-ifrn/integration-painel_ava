from django.utils.translation import gettext as _
import json
import urllib
import requests
import logging
import sentry_sdk
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.core.cache import cache
from django.contrib import auth
from a4.models import Usuario


logger = logging.getLogger(__name__)


def login(request: HttpRequest) -> HttpResponse:
    o = settings.OAUTH
    suap_url = (
        f"{o["AUTHORIZE_URL"]}?response_type=code&client_id={o["CLIENT_ID"]}&redirect_uri={o['REDIRECT_URI']}"
    )
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

    if request.GET.get("error") == "access_denied":
        return render(request, "a4/not_authorized.html")

    if "code" not in request.GET:
        raise Exception(_("O código de autenticação não foi informado."))

    logger.debug("OAUTH")
    logger.debug(OAUTH)

    access_token_request_data = {
        "grant_type": "authorization_code",
        "code": request.GET.get("code"),
        "redirect_uri": OAUTH["REDIRECT_URI"],
        "client_id": OAUTH["CLIENT_ID"],
        "client_secret": OAUTH["CLIENT_SECRET"],
    }
    logger.debug("access_token_request_data")
    logger.debug(access_token_request_data)
    access_token_response = requests.post(f"{OAUTH['TOKEN_URL']}", data=access_token_request_data, verify=OAUTH["VERIFY_SSL"])
    logger.debug("access_token_response_text")
    logger.debug(access_token_response.text)
    access_token_data = json.loads(access_token_response.text)
    logger.debug("access_token_data")
    logger.debug(access_token_data)

    if access_token_data.get("error_description") == "Mismatching redirect URI.":
        return render(request, "a4/mismatching_redirect_uri.html", {"error": access_token_data})

    user_info_request_header = {
        "Authorization": f"Bearer {access_token_data.get('access_token')}",
        "x-api-key": OAUTH["CLIENT_SECRET"],
    }
    logger.debug("user_info_request_header")
    logger.debug(user_info_request_header)
    user_info_response = requests.get(
        f"{OAUTH['USERINFO_URL']}?scope={access_token_data.get('scope', 'identificacao email documentos_pessoais')}",
        headers=user_info_request_header,
        verify=OAUTH["VERIFY_SSL"],
    )
    logger.debug("user_info_response.text")
    logger.debug(user_info_response.text)
    try:
        user_info_data = json.loads(user_info_response.text)
    except json.decoder.JSONDecodeError as e:
        sentry_sdk.capture_exception(e)
        if "__buscar_menu__" in user_info_response.text:
            return render(request, "a4/oauth_usuario_sem_vinculo.html")
        else:
            return render(request, "a4/oauth_error.html")

    logger.debug("user_info_data")
    logger.debug(user_info_data)

    username = user_info_data.get("identificacao", None)
    if username is None:
        return render(request, "a4/oauth_error.html")
    defaults = {
        "nome_registro": user_info_data.get("nome_registro"),
        "nome_social": user_info_data.get("nome_social"),
        "nome_usual": user_info_data.get("nome_usual"),
        "nome": user_info_data.get("nome"),
        "first_name": user_info_data.get("primeiro_nome"),
        "last_name": user_info_data.get("ultimo_nome"),
        "email": user_info_data.get("email_preferencial"),
        "email_corporativo": user_info_data.get("email"),
        "email_google_classroom": user_info_data.get("email_google_classroom"),
        "email_academico": user_info_data.get("email_academico"),
        "email_secundario": user_info_data.get("email_secundario"),
        "foto": user_info_data.get("foto"),
        "tipo_usuario": user_info_data.get("tipo_usuario"),
        "last_json": user_info_response.text,
    }

    user = Usuario.objects.filter(username=username).first()
    logger.debug(f"checking user: {user}")
    if user is None:
        is_superuser = Usuario.objects.count() == 0
        logger.debug(f"need to create user: {username}")
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
    auth.login(request, user)
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
