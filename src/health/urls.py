from django.urls import path
from .apps import HealthConfig
from .views import health, force_fail, force_db_fail


app_name = HealthConfig.name


urlpatterns = [
    path("health/", health, name="health"),
    path("force_fail/", force_fail, name="force_fail"),
    path("force_db_fail/", force_db_fail, name="force_db_fail"),
]
