from django.contrib.auth import views as auth_views
from django.urls import path
from django_suap_auth.views import SuapCallbackView, SuapLoginView

from .apps import A4Config
from .views import despersonificar, personificar

app_name = A4Config.name


urlpatterns = [
    path("login/", SuapLoginView.as_view(), name="login"),
    path("authenticate/", SuapCallbackView.as_view(), name="authenticate"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("personificar/<path:username>/", personificar, name="personificar"),
    path("despersonificar/", despersonificar, name="despersonificar"),
]
