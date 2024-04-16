from django.utils.translation import gettext as _
from django.conf import settings
from django.db.models import ForeignKey, PROTECT, CharField, DateTimeField, EmailField, TextField
from django.http import HttpRequest
from django.contrib.auth.models import AbstractUser, Group as OrignalGroup, UserManager
from django_better_choices import Choices
from simple_history.models import HistoricalRecords
from safedelete.models import SafeDeleteModel, SafeDeleteManager


def logged_user(request: HttpRequest):
    username = request.session.get("usuario_personificado", request.user.username)
    user = Usuario.objects.filter(username=username).first()
    return user if user is not None and user.is_authenticated and user.is_active else usuario_anonimo


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


TipoUsuario.kv = [{"id": p, "label": p.display} for p in TipoUsuario.values()]
TipoUsuario.COLABORADORES_KEYS = [
    TipoUsuario.DOCENTE,
    TipoUsuario.TECNICO,
    TipoUsuario.PRESTADOR,
]


class UsuarioManager(SafeDeleteManager, UserManager):
    pass


class Usuario(SafeDeleteModel, AbstractUser):
    username = CharField(
        _("IFRN-id"),
        max_length=150,
        unique=True,
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("A user with that IFRN-id already exists."),
        },
    )
    nome_registro = CharField(_("nome civil"), max_length=255, blank=True)
    nome_social = CharField(_("nome social"), max_length=255, null=True, blank=True)
    nome_usual = CharField(_("nome de apresentação"), max_length=255, null=True, blank=True)
    nome = CharField(_("nome no SUAP"), max_length=255, null=True, blank=True)
    tipo_usuario = CharField(_("tipo"), max_length=255, choices=TipoUsuario, null=True, blank=True)
    foto = CharField(_("URL da foto"), max_length=255, null=True, blank=True)
    email = EmailField(_("e-Mail preferêncial"), null=True, blank=False)
    email_secundario = EmailField(_("e-Mail pessoal"), null=True, blank=True)
    email_corporativo = EmailField(_("e-Mail corporativo"), null=True, blank=True)
    email_google_classroom = EmailField(_("e-Mail Gogole Classroom"), null=True, blank=True)
    email_academico = EmailField(_("e-Mail academico"), null=True, blank=True)
    first_login = DateTimeField(_("first login"), null=True, blank=True)
    last_json = TextField(_("último JSON"), null=True, blank=True)

    history = HistoricalRecords()

    objects = UsuarioManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.nome_usual} [{self.username}]"

    @property
    def show_name(self):
        return self.nome_usual if self.nome_usual is not None and self.nome_usual != "" else self.username

    @property
    def foto_url(self):
        if self.foto.startswith("http"):
            return self.foto
        return (
            f"{settings.OAUTH['BASE_URL']}{self.foto}" if self.foto else f"{settings.STATIC_URL}dashboard/img/user.png"
        )


Usuario._meta.icon = "fa fa-user"


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
