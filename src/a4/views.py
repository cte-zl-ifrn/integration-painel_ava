import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect

logger = logging.getLogger(__name__)


def personificar(request: HttpRequest, username: str):
    if not request.user.is_superuser:
        raise ValidationError("Só super usuários podem personificar")
    if "usuario_personificado" in request.session:
        raise ValidationError("Você já está personificando um usuário")

    User = get_user_model()
    u = get_object_or_404(User, username=username)
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
