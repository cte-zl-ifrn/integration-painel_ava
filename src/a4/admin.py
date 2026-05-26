from typing import Sequence

from django.contrib.admin import display, register, site
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from base.admin import BaseModelAdmin

from .models import Grupo, Usuario
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
                "fields": [("last_json"), ("vinculos"), ("observacao_erro_vinculo")],
                "description": _("JSONs com os dados do SUAP"),
            },
        ),
        (
            _("Settings"),
            {
                "fields": ["settings"],
                "description": _("Configurações do usuário"),
            },
        ),
    ]
    readonly_fields: Sequence[str] = [
        "date_joined",
        "first_login",
        "last_login",
        "last_json",
        "vinculos",
        "observacao_erro_vinculo",
    ]
    # autocomplete_fields: Sequence[str] = ['groups']
    resource_classes = [UsuarioResource]

    @display
    def auth(self, obj):
        result = "✅ " if obj.is_active else "❌ "
        result += _("Colaborador") if obj.is_staff else _("Usuário")
        result += " " + _("superusuário") if obj.is_superuser else ""
        return result

    @display
    def photo(self, obj):
        return format_html('<img width="56" height="56" src="{}"/>', obj.foto)

    @display(description=_("Ações"))
    def acoes(self, obj):
        if obj.is_superuser:
            return ""

        return format_html('<a href="{}">Personificar</a>', reverse("a4:personificar", args=[obj.username]))

    acoes.allow_tags = True
