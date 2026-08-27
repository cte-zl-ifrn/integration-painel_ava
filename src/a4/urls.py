from django.urls import path

from .apps import A4Config
from .views import despersonificar, personificar

app_name = A4Config.name


urlpatterns = [
    path("personificar/<path:username>/", personificar, name="personificar"),
    path("despersonificar/", despersonificar, name="despersonificar"),
]
