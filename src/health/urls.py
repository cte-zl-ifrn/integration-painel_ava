from django.urls import path
from .apps import HealthConfig
from .views import liveness, readiness, force_fail, force_db_fail


app_name = HealthConfig.name


urlpatterns = [
    path("health/", liveness, name="health"),
    path("probes/liveness/", liveness, name="liveness"),
    path("probes/readiness/", readiness, name="readiness"),
    path("sentry/force_fail/", force_fail, name="force_fail"),
    path("sentry/force_db_fail/", force_db_fail, name="force_db_fail"),
]
