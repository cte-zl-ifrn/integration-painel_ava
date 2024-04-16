from typing import Sequence, Union, Callable, Any
from functools import update_wrapper
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import path, reverse
from django.contrib.admin import ModelAdmin, register, site, display
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect
from base.admin import BaseModelAdmin
from .models import Usuario, Grupo
from .resources import UsuarioResource

site.unregister(Group)


@register(Grupo)
class GrupoAdmin(BaseModelAdmin):
    pass


@register(Usuario)
class UsuarioAdmin(BaseModelAdmin):
    list_display = ["username", "photo", "nome_usual", "email", "tipo_usuario", "auth", "acoes"]
    list_filter = ["tipo_usuario", "is_superuser", "is_active", "is_staff"]
    search_fields = ["username", "nome_usual", "email", "email_secundario"]
    fieldsets = [
        (
            _("Identificação"),
            {
                "fields": ["username", "nome_usual", "nome_registro", "nome_social", "foto"],
                "description": _("Identifica o usuário."),
            },
        ),
        (
            _("Autorização e autenticação"),
            {
                "fields": ["tipo_usuario", ("is_active", "is_staff", "is_superuser")],
                "description": _(
                    "Controla a identidade do usuário nos sistemas, qual seu papel e quais suas autorizações."
                ),
            },
        ),
        (
            _("Emails"),
            {
                "fields": [
                    ("email_secundario", "email"),
                    ("email_google_classroom", "email_academico"),
                ],
                "description": _("Conjunto de e-mails do usuário"),
            },
        ),
        (
            _("Dates"),
            {
                "fields": [("date_joined", "first_login", "last_login")],
                "description": _("Eventos relevantes relativos a este usuário"),
            },
        ),
        (
            _("Audit"),
            {
                "fields": [("last_json")],
                "description": _("JSON com os dados do SUAP"),
            },
        ),
    ]
    readonly_fields: Sequence[str] = ["date_joined", "first_login", "last_login", "last_json"]
    # autocomplete_fields: Sequence[str] = ['groups']
    resource_classes = [UsuarioResource]

    @display
    def auth(self, obj):
        result = (
            '<img src="/painel/static/admin/img/icon-yes.svg" alt="True"> '
            if obj.is_active
            else '<img src="/painel/static/admin/img/icon-no.svg" alt="False"> '
        )
        result += _("Colaborador") if obj.is_staff else _("Usuário")
        result += " " + _("superusuário") if obj.is_staff else ""
        return mark_safe(result)

    @display
    def photo(self, obj):
        return mark_safe(f'<img width="56" height="56" src="{obj.foto_url}" />')

    @display(description=_("Ações"))
    def acoes(self, obj):
        if not obj.is_superuser:
            url = reverse("a4:personificar", args=[obj.username])
            result = f'<a href="{url}">Personificar</a>'
        else:
            result = "-"
        return format_html(result)

    acoes.allow_tags = True
