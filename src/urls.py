import logging

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

from painel.v1.api import api as painel_api_v1
from painel.v2.api import api_v2 as painel_api_v2
from settings.indebug import DEBUG, TESTING_MODE

admin.site.site_title = "Painel AVA :.: Administração"
admin.site.site_header = admin.site.site_title


urlpatterns = [
    path(
        "",
        include(
            [
                path("admin/login/", RedirectView.as_view(url="/login/")),
                path("painel/", RedirectView.as_view(url="/")),
                path("admin/", admin.site.urls),
                path("api/v1/", painel_api_v1.urls),
                path("api/v2/", painel_api_v2.urls),
                path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
                path("", include("django_suap_auth.urls")),
                path("", include("a4.urls")),
                path("", include("health.urls")),
                path("", include("painel.urls")),
                path("", include("backup.urls")),
            ]
        ),
    ),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if DEBUG and not TESTING_MODE:
    try:
        from debug_toolbar.toolbar import debug_toolbar_urls

        urlpatterns += debug_toolbar_urls()
    except ImportError:
        logging.warning("Debug toolbar não encontrado, ignorando carregamento.")
