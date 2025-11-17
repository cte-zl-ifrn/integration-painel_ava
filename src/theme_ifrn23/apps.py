from tabnanny import verbose
from django.apps import AppConfig


class ThemeIfrn23Config(AppConfig):
    name: str = "theme_ifrn23"
    verbose_name: str = "Outono de 2023"
    icon: str = "fa fa-edit"
    is_painel_theme: bool = True
