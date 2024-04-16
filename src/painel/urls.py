from django.urls import path
from .apps import PainelConfig
from .views import dashboard, checkgrades
from painel.api import api


app_name = PainelConfig.name


urlpatterns = [
    path("api/v1/", api.urls),
    path("", dashboard, name="dashboard"),
    # path("diario/<id_diario>/syncs/", syncs, name="syncs"),
    path("diario/<id_ambiente>/<id_diario>/checkgrades/", checkgrades, name="checkgrades"),
]
