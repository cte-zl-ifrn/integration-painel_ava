from django.urls import path

from .api import api
from .apps import BackupConfig

app_name = BackupConfig.name


urlpatterns = [
    path("api/v1/", api.urls),
]
