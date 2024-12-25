from django.utils.translation import gettext as _
import re
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.forms import ValidationError
from django.db.models import BooleanField, URLField, CharField, DateTimeField, Model, TextField, ForeignKey, PROTECT
from django_better_choices import Choices
from simple_history.models import HistoricalRecords
from djrichtextfield.models import RichTextField


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


class Contrante(Model):
    url = URLField(_("URL"), max_length=256)
    url_logo = URLField(_("URL da logo"), max_length=256)
    titulo = CharField(_("título do painel"), max_length=256)
    nome_contratante = CharField(_("nome do contrante"), max_length=256)
    observacoes = RichTextField(_("observações"), null=True, blank=True)
    rodape = RichTextField(_("rodapé"), null=True, blank=True)
    css_personalizado = TextField(_("CSS personalizado"), null=True, blank=True)
    menu_personalizado = TextField(_("menu personalizado"), null=True, blank=True)
    regex_coordenacao = TextField(_("regex coordenação"), null=True, blank=True)
    active = BooleanField(_("ativo?"), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("contrante")
        verbose_name_plural = _("contrantes")
        ordering = ["titulo"]

    def __str__(self):
        return f"{self.titulo} ({self.url})"


class Ambiente(Model):
    def _c(color: str):
        return f"""<span style='background: {color}; color: #fff; padding: 1px 5px;
                                font-size: 95%; border-radius: 4px;'>{color}</span>"""

    contratante = ForeignKey(Contrante, on_delete=PROTECT, null=True, blank=False)
    cor_mestra = CharField(
        _("cor mestra"),
        max_length=255,
        help_text=mark_safe(
            f"""Escolha uma cor em RGB.
                Ex.: {_c('#a04ed0')} {_c('#396ba7')} {_c('#559c1a')}
                {_c('#fabd57')} {_c('#fd7941')} {_c('#f54f3b')} {_c('#2dcfe0')}"""
        ),
    )
    nome = CharField(_("nome do ambiente"), max_length=255)
    url = CharField(_("URL"), max_length=255)
    token = CharField(_("token"), max_length=255)
    active = BooleanField(_("ativo?"), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("ambiente")
        verbose_name_plural = _("ambientes")
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome}"

    @property
    def moodle_base_url(self):
        return self.url if self.url[-1:] != "/" else self.url[:-1]

    @property
    def moodle_base_api_url(self):
        return f"{self.base_url}/local/suap/api"

    @staticmethod
    def as_dict():
        return [
            {
                "id": a.id,
                "label": a.nome,
                "style": f"background-color: {a.cor_mestra}",
                "color": a.cor_mestra,
            }
            for a in Ambiente.objects.filter(active=True)
        ]

    @staticmethod
    def admins():
        return [
            {
                "id": a.id,
                "nome": re.subn("🟥 |🟦 |🟧 |🟨 |🟩 |🟪 ", "", a.nome)[0],
                "cor_mestra": a.cor_mestra,
                "url": f"{a.url}/admin/",
            }
            for a in Ambiente.objects.filter(active=True)
        ]


class Curso(Model):
    contratante = ForeignKey(Contrante, on_delete=PROTECT, null=True, blank=False)
    suap_id = CharField(_("ID do curso no SUAP"), max_length=255, unique=True)
    codigo = CharField(_("código do curso"), max_length=255, unique=True)
    nome = CharField(_("nome do curso"), max_length=255)
    descricao = CharField(_("descrição"), max_length=255)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("curso")
        verbose_name_plural = _("cursos")
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.codigo})"


class Popup(ActiveMixin, Model):
    contratante = ForeignKey(Contrante, on_delete=PROTECT, null=True, blank=False)
    titulo = CharField(_("título"), max_length=256)
    url = URLField(_("url"), max_length=256)
    mensagem = RichTextField(_("mensagem"))
    start_at = DateTimeField(_("inicia em"))
    end_at = DateTimeField(_("termina em"))
    active = BooleanField(_("ativo?"))
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

    def mostrando(self):
        sim = self.active and self.start_at <= now() and self.end_at >= now()
        return "✅" if sim else "❌"

    @staticmethod
    def activePopup():
        return Popup.objects.filter(active=True, start_at__lte=now(), end_at__gte=now()).first()
