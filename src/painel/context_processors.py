from typing import Dict
from django.conf import settings
from django.utils.translation import gettext as _
from django.http import HttpRequest
from django.urls import reverse
from a4.models import logged_user
from painel import get_installed_themes, get_active_themes
from painel.models import Ambiente, Popup


def popup(request: HttpRequest) -> Dict[str, Popup]:
    return {"popup": Popup.activePopup()}


def layout_settings(request: HttpRequest) -> dict:
    usuario_personificado = request.session.get("usuario_personificado", None)
    return {
        "logged_user": logged_user(request),
        "show_vlibras": settings.SHOW_VLIBRAS,
        "show_userway": settings.SHOW_USERWAY,
        "userway_account": settings.USERWAY_ACCOUNT,
        "personificando": usuario_personificado is not None,
        "last_startup": settings.LAST_STARTUP,
        "app_version": settings.APP_VERSION,
        "hostname": settings.HOSTNAME,
        "gtag": settings.GTAG_CODE if hasattr(settings, "GTAG_CODE") else False,
        "clarity": settings.CLARITY_CODE if hasattr(settings, "CLARITY_CODE") else False,
        "ambientes": Ambiente.cached(),
        "admins": Ambiente.admins(),
        "installed_themes": get_installed_themes(),
        "active_themes": get_active_themes(),
    }


def top_menu(request: HttpRequest) -> dict:
    staff_menus = (
        [
            {
                "label": _("Admin"),
                "url": reverse("admin:index"),
            },
        ]
        if request.user.is_staff
        else []
    )

    return {
        "layout_navbar_top_menu": [
            {
                "label": _("Início"),
                "url": reverse("painel:dashboard"),
            },
        ]
        + staff_menus
    }
