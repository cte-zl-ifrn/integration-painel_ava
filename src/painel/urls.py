from django.urls import path
from .apps import PainelConfig
from .views import dashboard, change_theme, change_menu_position, checkgrades, completed_tour, get_tour_status

from painel.api import api


app_name = PainelConfig.name


urlpatterns = [
    path("api/v1/", api.urls),
    path("", dashboard, name="dashboard"),
    path("change_theme/<theme>/", change_theme, name="change_theme"),
    path("settings/menu-position/", change_menu_position, name="menu_position"),
    path("diario/<id_ambiente>/<id_diario>/checkgrades/", checkgrades, name="checkgrades"),
    path("set_tour_completed/", completed_tour, name="set_tour_completed"),
    path("get_tour_status/", get_tour_status, name="get_tour_status"),

]
