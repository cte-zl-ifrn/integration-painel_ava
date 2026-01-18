from django.urls import path, include, re_path
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
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
                path("", include("a4.urls")),
                path("", include("health.urls")),
                path("", include("painel.urls")),
                path("", include("backup.urls")),
            ]
        ),
    ),
    # path("", RedirectView.as_view(url=settings.ROOT_URL_PATH)),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if DEBUG and not TESTING_MODE:
    try:
        from debug_toolbar.toolbar import debug_toolbar_urls

        urlpatterns += debug_toolbar_urls()
    except ImportError:
        pass
