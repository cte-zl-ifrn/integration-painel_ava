from django.utils.translation import gettext as _
from django.contrib.admin import register, StackedInline
from base.admin import BaseModelAdmin
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget
from import_export.fields import Field
from backup.models import ArquivoBackup, DonoBackup, DonoArquivoBackup


####
# Inlines
############
class DonoArquivoBackupInline(StackedInline):
    model = DonoArquivoBackup
    extra = 0
    tab = True


####
# Admins
############
@register(ArquivoBackup)
class ArquivoBackupAdmin(BaseModelAdmin):
    class Resource(ModelResource):
        class Meta:
            model = ArquivoBackup
            import_id_fields = ("nome_arquivo",)
            export_order = import_id_fields + (
                'nome_arquivo', 'curso_nome', 'curso_codigo', 
                'disciplina_codigo', 'disciplina_nome', 'disciplina_tipo', 
                'turma_codigo', 'ano_periodo', 'campus_sigla',
                'diario_id', 'diario_tipo', 'diario_codigo',
                'eh_sala_coordenacao', 'tem_certificado', 'carga_horaria',
                'url_com_dados', 'url_sem_dados',
            )
            fields = export_order
            skip_unchanged = True
    list_display = ["nome_arquivo", "curso_nome", "disciplina_nome"]
    search_fields = list_display + []
    list_filter = [
        # ('curso_nome', CursoNomeFilter),
        # ('disciplina_nome', AutocompleteListFilter),
        # ('ano_periodo', AutocompleteListFilter),
        # ('turma_codigo', AutocompleteListFilter),
        # ('campus_sigla', AutocompleteListFilter),
        # ('carga_horaria', AutocompleteListFilter),
        'eh_sala_coordenacao',
        'tem_certificado',
    ]
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
