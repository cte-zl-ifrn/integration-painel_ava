from django.urls import path, include, re_path
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from settings.indebug import DEBUG

admin.site.site_title = "Painel AVA :.: Administração"
admin.site.site_header = admin.site.site_title

urlpatterns = [
    path(
        "",
        include(
            [
                path("admin/login/", RedirectView.as_view(url="/login/")),
                path("painel/", RedirectView.as_view(url="/")),
                path("djrichtextfield/", include("djrichtextfield.urls")),
                path("admin/", admin.site.urls),
                path("", include("a4.urls")),
                path("", include("health.urls")),
                path("", include("painel.urls")),
            ]
        ),
    ),
    # path("", RedirectView.as_view(url=settings.ROOT_URL_PATH)),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if DEBUG:
    try:
        import debug_toolbar

        urlpatterns.append(path(f"{settings.ROOT_URL_PATH}__debug__/", include(debug_toolbar.urls)))
    except ImportError:
        pass
