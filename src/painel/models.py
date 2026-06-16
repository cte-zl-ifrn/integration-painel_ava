import logging
import re

from django.core.cache import cache
from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    IntegerField,
    Model,
    TextField,
    URLField,
)
from django.forms import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django_better_choices import Choices
from simple_history.models import HistoricalRecords

logger = logging.getLogger(__name__)


class BaseChoices(Choices):
    @classmethod
    @property
    def kv(cls):
        return [{"id": p, "label": p.display} for p in cls.values()]


class Situacao(Choices):
    IN_PROGRESS = Choices.Value(_("✳️ Diários em andamento"), value="inprogress")
    FUTURE = Choices.Value(_("🗓️ Diários a iniciar"), value="future")
    PAST = Choices.Value(_("📕 Encerrados pelo professor"), value="past")
    FAVOURITES = Choices.Value(_("⭐ Meus diários favoritos"), value="favourites")
    ALL = Choices.Value(_("♾️ Todos os diários (lento)"), value="allincludinghidden")


class ActiveMixin:
    @property
    def active_icon(self):
        return "✅" if self.active else "⛔"


class Theme(ActiveMixin, Model):
    nome = CharField(_("nome do theme"), max_length=255)
    apelido = CharField(_("apelido"), max_length=255)
    active = BooleanField(_("ativo?"), default=True)

    class Meta:
        verbose_name = _("tema")
        verbose_name_plural = _("temas")
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} - {self.active_icon}"


class Ambiente(ActiveMixin, Model):

    nome = CharField(_("nome do ambiente"), max_length=255)
    url = CharField(_("URL"), max_length=255)
    token = CharField(_("token"), max_length=255)
    cor_mestra = CharField(
        _("cor mestra"),
        max_length=255,
        help_text="""Escolha uma cor em RGB. Ex.: #a04ed0 #396ba7 #559c1a #fabd57 #fd7941 #f54f3b #2dcfe0""",
    )
    active = BooleanField(_("ativo?"), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("ambiente")
        verbose_name_plural = _("ambientes")
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.debug("limpando o cache dos ambientes")
        cache.delete("ambientes")

    @property
    def moodle_base_url(self):
        return self.url if self.url[-1:] != "/" else self.url[:-1]

    @property
    def moodle_base_api_url(self):
        return f"{self.moodle_base_url}/admin/tool/painelava/api"

    @staticmethod
    def as_dict():
        return [
            {
                "id": a.id,
                "label": a.nome,
                "style": f"background-color: {a.cor_mestra}",
                "color": a.cor_mestra,
            }
            for a in Ambiente.cached()
        ]

    @staticmethod
    def cached() -> list:
        all_ambientes = cache.get("ambientes")
        if all_ambientes is None:
            all_ambientes = [x for x in Ambiente.objects.filter(active=True)]
            logger.debug(f"colocando no cache os ambientes: {all_ambientes}")
            cache.set("ambientes", all_ambientes)
        return all_ambientes

    @staticmethod
    def admins():
        return [
            {
                "id": a.id,
                "nome": re.subn("🟥 |🟦 |🟧 |🟨 |🟩 |🟪 ", "", a.nome)[0],
                "cor_mestra": a.cor_mestra,
                "url": f"{a.url}/admin/",
            }
            for a in Ambiente.cached()
        ]


class Curso(Model):
    codigo = CharField(_("código do curso"), max_length=255, unique=True)
    nome = CharField(_("nome do curso"), max_length=255)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("curso")
        verbose_name_plural = _("cursos")
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f"curso:{self.codigo}")


class Popup(ActiveMixin, Model):
    titulo = CharField(_("título"), max_length=256)
    url = URLField(_("url"), max_length=256)
    mensagem = TextField(_("mensagem"))
    start_at = DateTimeField(_("inicia em"))
    end_at = DateTimeField(_("termina em"))
    active = BooleanField(_("ativo?"), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("popup")
        verbose_name_plural = _("popups")
        ordering = ["start_at", "titulo"]

    def clean(self):
        if self.start_at and self.end_at and self.start_at > self.end_at:
            raise ValidationError({"end_at": _("O término deve ser maior do que o início.")})

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)
        cache.delete("popups")

    def mostrando(self):
        sim = self.active and self.start_at <= now() and self.end_at >= now()
        return "✅" if sim else "❌"

    @staticmethod
    def cached() -> list:
        all_instances = cache.get("popups")
        if all_instances is None:
            all_instances = [x for x in Popup.objects.filter(active=True, start_at__lte=now(), end_at__gte=now())]
            logger.debug(f"colocando no cache os popups: {all_instances}")
            cache.set("popups", all_instances)
        return all_instances or []

    @staticmethod
    def activePopup():
        return next(iter(Popup.cached()), None)


class ConfiguracaoAba(Model):
    chave = CharField(
        _("chave (Moodle)"),
        max_length=50,
        unique=True,
        help_text=_("O nome exato do sala_tipo enviado pelo Moodle (ex: diarios, praticas, autoinscricoes, tcc)"),
    )
    nome_desktop = CharField(
        _("nome no desktop"), max_length=100, help_text=_("Ex: Meus Diários, Salas de Coordenação")
    )
    nome_mobile = CharField(
        _("nome no mobile"), max_length=50, help_text=_("Nome curto para telas menores. Ex: Diários, Coordenações")
    )
    ordem = IntegerField(
        _("ordem"),
        default=99,
        help_text=_("Números menores aparecem primeiro (ex: 1 para Diários, 2 para Coordenações)."),
    )
    sempre_visivel = BooleanField(
        _("sempre visível?"),
        default=False,
        help_text=_("Se marcado, a aba aparece mesmo que o usuário tenha 0 cursos nela."),
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("configuração de aba")
        verbose_name_plural = _("configurações de abas")
        ordering = ["ordem", "chave"]

    def __str__(self):
        return f"{self.nome_desktop} ({self.chave})"
