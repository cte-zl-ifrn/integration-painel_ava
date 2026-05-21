from django.utils.translation import gettext as _
from django.contrib.admin import register, TabularInline, StackedInline
from base.admin import BaseModelAdmin
from painel.models import Ambiente, Curso, Popup, Theme, ConfiguracaoAba


####
# Inlines
####


####
# Admins
####
@register(Ambiente)
class AmbienteAdmin(BaseModelAdmin):
    list_display = ["nome", "url", "active"]
    search_fields = ["nome", "url"]
    list_filter = ["active"] + BaseModelAdmin.list_filter


@register(Curso)
class CursoAdmin(BaseModelAdmin):
    list_display = ["codigo", "nome"]
    search_fields = ["codigo", "nome"]
    list_filter = BaseModelAdmin.list_filter


@register(Popup)
class PopupAdmin(BaseModelAdmin):
    list_display = ["titulo", "start_at", "end_at"]
    search_fields = ["titulo", "url", "mensagem"]
    list_filter = ["active"] + BaseModelAdmin.list_filter

@register(Theme)
class ThemeAdmin(BaseModelAdmin):
    list_display = ["nome", "active"]
    search_fields = ["nome"]
    list_filter = ["active"] + BaseModelAdmin.list_filter

@register(ConfiguracaoAba)
class ConfiguracaoAbaAdmin(BaseModelAdmin):
    list_display = ["chave", "nome_desktop", "nome_mobile", "ordem", "sempre_visivel"]
    list_editable = ["nome_desktop", "nome_mobile", "ordem", "sempre_visivel"]
    search_fields = ["chave", "nome_desktop", "nome_mobile"]
    list_filter = ["sempre_visivel"] + BaseModelAdmin.list_filter