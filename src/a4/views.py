from django.utils.translation import gettext as _
import json
import urllib
import requests
from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from a4.models import Usuario


def login(request: HttpRequest) -> HttpResponse:
    o = settings.OAUTH
    suap_url = f"{o["BASE_URL"]}/o/authorize/?response_type=code&client_id={o["CLIENT_ID"]}&redirect_uri={o['REDIRECT_URI']}"
    return redirect(suap_url)


def authenticate(request: HttpRequest) -> HttpResponse:
    OAUTH = settings.OAUTH

    if request.GET.get("error") == "access_denied":
        return render(request, "a4/not_authorized.html")

    if "code" not in request.GET:
        raise Exception(_("O código de autenticação não foi informado."))

    access_token_request_data = {
        "grant_type": "authorization_code",
        "code": request.GET.get("code"),
        "redirect_uri": OAUTH["REDIRECT_URI"],
        "client_id": OAUTH["CLIENT_ID"],
        "client_secret": OAUTH["CLIENT_SECRET"],
    }

    token_str = requests.post(f"{OAUTH['BASE_URL']}/o/token/", data=access_token_request_data, verify=OAUTH["VERIFY_SSL"]).text
    request_data = json.loads(token_str)

    if request_data.get("error_description") == "Mismatching redirect URI.":
        return render(request, "a4/mismatching_redirect_uri.html", {"error": request_data})

    headers = {
        "Authorization": f"Bearer {request_data.get('access_token')}",
        "x-api-key": OAUTH["CLIENT_SECRET"],
    }

    response = requests.get(
        f"{OAUTH['BASE_URL']}/api/v1/userinfo/?scope={request_data.get('scope')}",
        headers=headers,
        verify=OAUTH["VERIFY_SSL"],
    )
    print(response.text)
    response_data = json.loads(response.text)

    username = response_data["identificacao"]
    user = Usuario.objects.filter(username=username).first()
    defaults = {
        "nome_registro": response_data.get("nome_registro"),
        "nome_social": response_data.get("nome_social"),
        "nome_usual": response_data.get("nome_usual"),
        "nome": response_data.get("nome"),
        "first_name": response_data.get("primeiro_nome"),
        "last_name": response_data.get("ultimo_nome"),
        "email": response_data.get("email_preferencial"),
        "email_corporativo": response_data.get("email"),
        "email_google_classroom": response_data.get("email_google_classroom"),
        "email_academico": response_data.get("email_academico"),
        "email_secundario": response_data.get("email_secundario"),
        "foto": response_data.get("foto"),
        "tipo_usuario": response_data.get("tipo_usuario"),
        "last_json": response.text,
    }
    if user is None:
        is_superuser = Usuario.objects.count() == 0
        user = Usuario.objects.create(
            username=username,
            is_superuser=is_superuser,
            is_staff=is_superuser,
            first_login=now(),
            **defaults,
        )
    else:
        user = Usuario.objects.filter(username=username).first()
        if user.first_login is None:
            user.first_login = now()
            user.save()
        Usuario.objects.filter(username=username).update(**defaults)
    auth.login(request, user)
    return redirect("painel:dashboard")


def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)
    return redirect(f"{settings.LOGOUT_REDIRECT_URL}?next={urllib.parse.quote_plus(settings.LOGIN_REDIRECT_URL)}")


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
