from django.utils.translation import gettext as _
import re
import logging
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.forms import ValidationError
from django.db.models import BooleanField, URLField, CharField, DateTimeField, Model, TextField, ForeignKey, PROTECT
from django.core.cache import cache
from django_better_choices import Choices
from simple_history.models import HistoricalRecords
from djrichtextfield.models import RichTextField


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
    active = BooleanField(_("ativo?"), default=True)

    class Meta:
        verbose_name = _("tema")
        verbose_name_plural = _("temas")
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} - {self.active_icon}"


class Contrante(ActiveMixin, Model):
    url = URLField(_("URL"), max_length=256)
    url_logo = URLField(_("URL da logo"), max_length=256)
    titulo = CharField(_("título do painel"), max_length=256)
    nome_contratante = CharField(_("nome do contrante"), max_length=256)
    observacoes = RichTextField(_("observações"), null=True, blank=True)
    rodape = RichTextField(_("rodapé"), null=True, blank=True)
    css_personalizado = TextField(_("CSS personalizado"), null=True, blank=True)
    menu_personalizado = TextField(_("menu personalizado"), null=True, blank=True)
    regex_coordenacao = TextField(_("regex coordenação"), null=True, blank=True)
    default_theme = ForeignKey(Theme, on_delete=PROTECT, null=True, blank=False)
    useraway_active = BooleanField(_("ativar userway?"), default=False)
    useraway_account = TextField(_("código do userway"), null=True, blank=True)
    vlibras_active = TextField(_("ativar vlibras"), null=True, blank=True)
    active = BooleanField(_("ativo?"), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("contrante")
        verbose_name_plural = _("contrantes")
        ordering = ["titulo"]

    def __str__(self):
        return f"{self.titulo} ({self.url})"


class Ambiente(ActiveMixin, Model):
    def _c(color: str):
        return f"""<span style='background: {color}; color: #fff; padding: 1px 5px;
                                font-size: 95%; border-radius: 4px;'>{color}</span>"""

    contratante = ForeignKey(Contrante, on_delete=PROTECT, null=True, blank=False)
    nome = CharField(_("nome do ambiente"), max_length=255)
    url = CharField(_("URL"), max_length=255)
    token = CharField(_("token"), max_length=255)
    cor_mestra = CharField(
        _("cor mestra"),
        max_length=255,
        help_text=mark_safe(
            f"""Escolha uma cor em RGB.
                Ex.: {_c('#a04ed0')} {_c('#396ba7')} {_c('#559c1a')}
                {_c('#fabd57')} {_c('#fd7941')} {_c('#f54f3b')} {_c('#2dcfe0')}"""
        ),
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
        logger.debug(f"limpando o cache dos ambientes")
        cache.delete("ambientes")

    @property
    def moodle_base_url(self):
        return self.url if self.url[-1:] != "/" else self.url[:-1]

    @property
    def moodle_base_api_url(self):
        return f"{self.moodle_base_url}/local/suap/api"

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
    contratante = ForeignKey(Contrante, on_delete=PROTECT, null=True, blank=False)
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
        logger.debug(f"limpando o cache dos cursos")
        cache.delete("cursos")

    @staticmethod
    def cached() -> list:
        all_instances = cache.get("cursos")
        if all_instances is None:
            all_instances = [x for x in Curso.objects.all()]
            logger.debug(f"colocando no cache os cursos: {all_instances}")
            cache.set("cursos", all_instances)
        return all_instances or []

    @staticmethod
    def cached_by_codigos(codigos: list) -> list:
        return [x for x in Curso.cached() if x.codigo in codigos]


class Popup(ActiveMixin, Model):
    contratante = ForeignKey(Contrante, on_delete=PROTECT, null=True, blank=False)
    titulo = CharField(_("título"), max_length=256)
    url = URLField(_("url"), max_length=256)
    mensagem = RichTextField(_("mensagem"))
    start_at = DateTimeField(_("inicia em"))
    end_at = DateTimeField(_("termina em"))
    active = BooleanField(_("ativo?"), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("popup")
        verbose_name_plural = _("popups")
        ordering = ["start_at", "titulo"]

    def __str__(self):
        return f"{self.titulo} - {self.active_icon}"

    def save(self, *args, **kwargs):
        if self.start_at > self.end_at:
            return ValidationError("O término deve ser maior do que o início.")
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

class AddedTheme(ActiveMixin, Model):
    contratante = ForeignKey(Contrante, on_delete=PROTECT)
    theme = ForeignKey(Theme, on_delete=PROTECT)
    active = BooleanField(_("ativo?"), default=True)

    class Meta:
        verbose_name = _("tema autorizado")
        verbose_name_plural = _("temas autorizados")
        unique_together = ("contratante", "theme")

    def __str__(self):
        return f"{self.theme} - {self.contratante} - {self.active_icon}"
