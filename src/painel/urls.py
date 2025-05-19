from django.urls import path
from .apps import PainelConfig
from .views import dashboard, change_theme, checkgrades
from painel.api import api


app_name = PainelConfig.name


urlpatterns = [
    path("api/v1/", api.urls),
    path("", dashboard, name="dashboard"),
    path("change_theme/<theme>/", change_theme, name="change_theme"),
    path("diario/<id_ambiente>/<id_diario>/checkgrades/", checkgrades, name="checkgrades"),
]
