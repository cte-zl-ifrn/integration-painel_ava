from django.urls import path
from .apps import BackupConfig
from .views import dashboard, change_theme, change_menu_position, checkgrades, completed_tour, get_tour_status
from .api import api


app_name = BackupConfig.name


urlpatterns = [
    path("api/v1/", api.urls),
]
