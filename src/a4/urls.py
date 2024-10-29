from django.urls import path
from .apps import A4Config
from .views import login, authenticate, logout
from .views import personificar, despersonificar


app_name = A4Config.name


urlpatterns = [
    path("login/", login, name="login"),
    path("authenticate/", authenticate, name="authenticate"),
    path("logout/", logout, name="logout"),
    path("personificar/<path:username>/", personificar, name="personificar"),
    path("despersonificar/", despersonificar, name="despersonificar"),
]
