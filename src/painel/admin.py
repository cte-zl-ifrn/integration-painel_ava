from django.utils.translation import gettext as _
from django.db.models import Model
from django.contrib.admin import register, display
from django.utils.safestring import mark_safe
from base.admin import BaseModelAdmin
from painel.models import Contrante, Ambiente, Curso, Popup
from painel.resources import AmbienteResource


####
# Admins
####


@register(Contrante)
class ContranteAdmin(BaseModelAdmin):
    list_display = ["url", "titulo"]
    history_list_display = list_display
    field_to_highlight = list_display[0]
    search_fields = ["titulo", "url", "nome_contratante", "observacoes", "rodape"]
    list_filter = [
        "active",
    ] + BaseModelAdmin.list_filter


@register(Ambiente)
class AmbienteAdmin(BaseModelAdmin):
    list_display = ["nome", "cores", "url", "active"]
    history_list_display = list_display
    field_to_highlight = list_display[0]
    search_fields = ["nome", "url"]
    list_filter = [
        "active",
    ] + BaseModelAdmin.list_filter
    fieldsets = [
        (_("Identificação"), {"fields": ["nome", "cor_mestra"]}),
        (_("Integração"), {"fields": ["active", "url", "token"]}),
    ]
    resource_classes = [AmbienteResource]

    @display(description="Cores")
    def cores(self, obj):
        return mark_safe(f"<span style='background: {obj.cor_mestra};'>&nbsp;&nbsp;&nbsp;</span>")


@register(Curso)
class CursoAdmin(BaseModelAdmin):
    list_display = ["codigo", "nome"]
    search_fields = ["suap_id", "codigo", "nome", "descricao"]
    list_filter = BaseModelAdmin.list_filter


@register(Popup)
class PopupAdmin(BaseModelAdmin):
    list_display = ["titulo", "mostrando", "start_at", "end_at", "active"]
    search_fields = ["titulo", "mensagem", "url"]
    list_filter = [
        "active",
        "start_at",
        "end_at"
    ] + BaseModelAdmin.list_filter
