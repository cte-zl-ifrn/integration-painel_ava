from django.utils.translation import gettext as _
import logging
from django.db.models import BooleanField, URLField, CharField, Model, ForeignKey, EmailField, PROTECT


logger = logging.getLogger(__name__)


class ArquivoBackup(Model):
    nome_arquivo = CharField(_("nome do arquivo"), max_length=2560, unique=True)
    curso_nome = CharField(_("nome do curso"), max_length=2560)
    curso_codigo = CharField(_("código do curso"), max_length=2560, null=True, blank=True)
    disciplina_codigo = CharField(_("código da disciplina"), max_length=2560, null=True, blank=True)
    disciplina_nome = CharField(_("nome da disciplina"), max_length=2560, null=True, blank=True)
    disciplina_tipo = CharField(_("tipo da disciplina"), max_length=2560, null=True, blank=True)
    turma_codigo = CharField(_("código da turma"), max_length=2560, null=True, blank=True)
    ano_periodo = CharField(_("ano/periodo"), max_length=2560, null=True, blank=True)
    campus_sigla = CharField(_("sigla do campus"), max_length=2560, null=True, blank=True)
    diario_id = CharField(_("id do diário"), max_length=2560, null=True, blank=True)
    diario_tipo = CharField(_("tipo de diário"), max_length=2560, null=True, blank=True)
    diario_codigo = CharField(_("código do diário"), max_length=2560, null=True, blank=True)
    eh_sala_coordenacao = BooleanField(_("é sala de coordenação"), default=False)
    tem_certificado = BooleanField(_("tem certificado"), default=False)
    carga_horaria = CharField(_("carga horária"), max_length=2560, null=True, blank=True)
    url_com_dados = URLField(_("URL com dados"), max_length=2560, unique=True)
    url_sem_dados = URLField(_("URL sem dados"), max_length=2560, unique=True)

    class Meta:
        verbose_name = _("arquivo")
        verbose_name_plural = _("arquivos")

    def __str__(self):
        return f"{self.curso_nome} - {self.nome_arquivo}"


class DonoBackup(Model):
    username = CharField(_("username"), max_length=256, unique=True)
    nome = CharField(_("nome do dono do backup"), max_length=2560)
    email = EmailField(_("e-mail"), max_length=2560, null=True, blank=True)

    class Meta:
        verbose_name = _("dono")
        verbose_name_plural = _("donos")

    def __str__(self):
        return self.username


class DonoArquivoBackup(Model):
    arquivo_backup = ForeignKey(ArquivoBackup, on_delete=PROTECT)
    dono_backup = ForeignKey(DonoBackup, on_delete=PROTECT)
    papel = CharField(_("papel original no curso"), max_length=2560, null=True, blank=True)

    class Meta:
        verbose_name = _("permissão")
        verbose_name_plural = _("permissões")

    def __str__(self):
        return f"{self.arquivo_backup} por '{self.dono_backup}'"
