from tabnanny import verbose
from django.apps import AppConfig


class ThemeIfrn25Config(AppConfig):
    name: str = "theme_ifrn25"
    verbose_name: str = "Outono de 2025"
    icon: str = "fa fa-edit"
    is_painel_theme: bool = True

