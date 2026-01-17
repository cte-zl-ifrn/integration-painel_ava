from django.utils.translation import gettext as _
from django.db.models import Model
from django.contrib.admin import register, display, TabularInline, StackedInline
from django.utils.safestring import mark_safe
from base.admin import BaseModelAdmin
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget
from import_export.fields import Field
from painel.models import Contrante, Ambiente, Curso, Popup, Theme, AddedTheme
from painel.models import ArquivoBackup, DonoBackup, DonoArquivoBackup
from painel.resources import AmbienteResource


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


class DonoArquivoBackupInline(StackedInline):
    model = DonoArquivoBackup
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


@register(ArquivoBackup)
class ArquivoBackupAdmin(BaseModelAdmin):
    class Resource(ModelResource):
        class Meta:
            model = ArquivoBackup
            import_id_fields = ("nome_arquivo",)
            export_order = import_id_fields + ("nome_curso", "url_com_dados", "url_sem_dados")
            fields = export_order
            skip_unchanged = True
    list_display = ["nome_curso", "nome_arquivo"]
    search_fields = ["nome_curso", "nome_arquivo"]
    inlines=[DonoArquivoBackupInline]
    resource_classes = [Resource]


@register(DonoBackup)
class DonoBackupAdmin(BaseModelAdmin):
    class Resource(ModelResource):
        class Meta:
            model = DonoBackup
            import_id_fields = ("username",)
            export_order = import_id_fields + ("email", "nome")
            fields = export_order
            skip_unchanged = True
    list_display = ["username", "nome", "email"]
    search_fields = ["username", "nome", "email"]
    inlines=[DonoArquivoBackupInline]
    resource_classes = [Resource]


@register(DonoArquivoBackup)
class DonoArquivoAdmin(BaseModelAdmin):
    class DonoArquivoBackupResource(ModelResource):
        arquivo_backup = Field("arquivo_backup", "arquivo_backup", ForeignKeyWidget(ArquivoBackup, field=ArquivoBackupAdmin.Resource.Meta.import_id_fields[0]))
        dono_backup = Field("dono_backup", "dono_backup", ForeignKeyWidget(DonoBackup, field=DonoBackupAdmin.Resource.Meta.import_id_fields[0]))
        class Meta:
            model = DonoArquivoBackup
            import_id_fields = ("arquivo_backup", "dono_backup")
            export_order = import_id_fields
            fields = export_order
            skip_unchanged = True
    list_display = ["arquivo_backup", "dono_backup"]
    search_fields = ["arquivo_backup", "dono_backup"]
    resource_classes = [DonoArquivoBackupResource]
