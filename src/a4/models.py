from django.utils.translation import gettext as _
import logging
from django.conf import settings
from django.db.models import ForeignKey, PROTECT, CharField, DateTimeField, EmailField, TextField, JSONField
from django.http import HttpRequest
from django.core.cache import cache
from django.contrib.auth.models import AbstractUser, Group as OrignalGroup, UserManager
from django_better_choices import Choices
from simple_history.models import HistoricalRecords
from safedelete.models import SafeDeleteModel, SafeDeleteManager


logger = logging.getLogger(__name__)


def logged_user(request: HttpRequest):
    username = request.session.get("usuario_personificado", request.user.username)
    user = Usuario.cached(username)
    return user if user is not None else usuario_anonimo


class Grupo(SafeDeleteModel, OrignalGroup):
    history = HistoricalRecords()


class TipoUsuario(Choices):
    DOCENTE = Choices.Value(_("Servidor (Docente)"), value="Servidor (Docente)")
    TECNICO = Choices.Value(
        _("Servidor (Técnico-Administrativo)"),
        value="Servidor (Técnico-Administrativo)",
    )
    PRESTADOR = Choices.Value(_("Prestador de Serviço"), value="Prestador de Serviço")
    ALUNO = Choices.Value(_("Aluno"), value="Aluno")
    DESCONHECIDO = Choices.Value(_("Desconhecido"), value=None)


class UsuarioManager(SafeDeleteManager, UserManager):
    pass


class Usuario(SafeDeleteModel, AbstractUser):
    username = CharField(
        _("IFRN-id"),
        max_length=2560,
        unique=True,
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("A user with that IFRN-id already exists."),
        },
    )
    first_name = CharField(_("primeiro nome"), max_length=2560, null=True, blank=True)
    last_name = CharField(_("último nome"), max_length=2560, null=True, blank=True)
    nome_registro = CharField(_("nome civil"), max_length=2560, null=True, blank=True)
    nome_social = CharField(_("nome social"), max_length=2560, null=True, blank=True)
    nome_usual = CharField(_("nome de apresentação"), max_length=2560, null=True, blank=True)
    nome = CharField(_("nome no SUAP"), max_length=2560, null=True, blank=True)
    tipo_usuario = CharField(_("tipo"), max_length=2560, choices=TipoUsuario, null=True, blank=True)
    foto = CharField(_("URL da foto"), max_length=2560, null=True, blank=True)
    email = EmailField(_("e-Mail preferêncial"), max_length=2560, null=True, blank=False)
    email_secundario = EmailField(_("e-Mail pessoal"), max_length=2560, null=True, blank=True)
    email_corporativo = EmailField(_("e-Mail corporativo"), max_length=2560, null=True, blank=True)
    email_google_classroom = EmailField(_("e-Mail Gogole Classroom"), max_length=2560, null=True, blank=True)
    email_academico = EmailField(_("e-Mail academico"), max_length=2560, null=True, blank=True)
    first_login = DateTimeField(_("first login"), null=True, blank=True)
    last_json = TextField(_("último JSON"), null=True, blank=True)
    settings = JSONField(_("configurações"), null=True, blank=True)

    history = HistoricalRecords()

    objects = UsuarioManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    class AdminMeta:
        icon = "fa fa-user"

    def __str__(self):
        return f"{self.nome_usual} [{self.username}]"

    @property
    def show_name(self):
        return self.nome_usual if self.nome_usual is not None and self.nome_usual != "" else self.username

    @property
    def theme_selected(self) -> str:
        if self.settings is not None and "theme" in self.settings and "selected" in self.settings["theme"]:
            return self.settings["theme"]["selected"]
        return "ifrn23"
    
    @property
    def dyslexia_friendly(self) -> bool:
        try:
            return self.settings.get("accessibility", {}).get("dyslexia_friendly", False)
        except AttributeError:
            return False

    @property
    def remove_justify(self) -> bool:
        try:
            return self.settings.get("accessibility", {}).get("remove_justify", False)
        except AttributeError:
            return False

    @property
    def highlight_links(self) -> bool:
        try:
            return self.settings.get("accessibility", {}).get("highlight_links", False)
        except AttributeError:
            return False

    @property
    def stop_animations(self) -> bool:
        try:
            return self.settings.get("accessibility", {}).get("stop_animations", False)
        except AttributeError:
            return False

    @property
    def hidden_illustrative_image(self) -> bool:
        try:
            return self.settings.get("accessibility", {}).get("hidden_illustrative_image", False)
        except AttributeError:
            return False

    @property
    def big_cursor(self) -> bool:
        try:
            return self.settings.get("accessibility", {}).get("big_cursor", False)
        except AttributeError:
            return False

    @property
    def vlibras_active(self) -> bool:
        try:
            return self.settings.get("accessibility", {}).get("vlibras_active", True)
        except AttributeError:
            return True

    @property
    def high_line_height(self) -> bool:
        try:
            return self.settings.get("accessibility", {}).get("high_line_height", False)
        except AttributeError:
            return False

    @property
    def zoom_level(self) -> int:
        try:
            return int(self.settings.get("accessibility", {}).get("zoom_level", 100))
        except (AttributeError, ValueError, TypeError):
            return 100

    #TODO: cor
    
    @property
    def menu_position(self) -> str:
        if self.settings and "menu_position" in self.settings:
            return self.settings["menu_position"]
        return "bottom"

    @property
    def foto_url(self):
        if self.foto is None or "" == self.foto:
            return f"{settings.STATIC_URL}theme/{self.theme_selected}/img/user.png"
        if not self.foto.lower().startswith("http"):
            return f"{settings.OAUTH['BASE_URL']}{self.foto}"
        return self.foto

    @staticmethod
    def cached(username: str) -> AbstractUser:
        userkey = f"username:{username}"
        user = cache.get(userkey)
        if user is None:
            user = Usuario.objects.filter(username=username).first()
            if user is not None and user.is_authenticated and user.is_active:
                logger.debug(f"colocando no cache o usuário: {username}")
                cache.set(userkey, user)
        return user


class UsuarioAnonimo:
    username = "anonimo"
    nome_registro = "Anônimo"
    nome_social = "Anônimo"
    nome_usual = "Anônimo"
    nome = "Anônimo"
    show_name = "Anônimo"
    tipo_usuario = "Anônimo"
    foto = None
    email = None
    email_secundario = None
    email_corporativo = None
    email_google_classroom = None
    email_academico = None
    first_login = None
    is_authenticated = False
    is_active = False

    def __str__(self):
        return self.show_name


usuario_anonimo = UsuarioAnonimo()
