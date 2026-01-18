from tabnanny import verbose
from django.apps import AppConfig


class BackupConfig(AppConfig):
    name = "backup"
    verbose_name = "Backup"
    icon = "fa fa-database"
