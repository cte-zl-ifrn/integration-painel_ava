from django.utils.translation import gettext as _
from django.db.models import Model
from django.contrib.admin import register, display, TabularInline, StackedInline
from django.utils.safestring import mark_safe
from base.admin import BaseModelAdmin
from painel.models import Contrante, Ambiente, Curso, Popup, Theme, AddedTheme
from painel.resources import AmbienteResource
from unfold.admin import StackedInline, TabularInline

####
# Inlines
####


class AddedThemeInline(TabularInline):
    model = AddedTheme
    list_display = ["theme", "active"]
    extra = 0
    tab = True

class AmbienteInline(TabularInline):
    model = Ambiente
    # list_display = ["theme", "active"]
    extra = 0
    tab = True


class CursoAmbienteInline(TabularInline):
    model = Curso
    # list_display = ["theme", "active"]
    extra = 0
    tab = True


class PopupAmbienteInline(StackedInline):
    model = Popup
    # list_display = ["theme", "active"]
    extra = 0
    tab = True


####
# Admins
####


@register(Contrante)
class ContranteAdmin(BaseModelAdmin):
    list_display = ["titulo", "url"]
    history_list_display = list_display
    field_to_highlight = list_display[0]
    search_fields = ["titulo", "url", "nome_contratante", "observacoes", "rodape"]
    list_filter = ["active"] + BaseModelAdmin.list_filter
    inlines = [AmbienteInline, CursoAmbienteInline, PopupAmbienteInline, AddedThemeInline]


@register(Theme)
class ThemeAdmin(BaseModelAdmin):
    list_display = ["nome", "active"]
    search_fields = ["nome"]
    list_filter = ["active"] + BaseModelAdmin.list_filter
