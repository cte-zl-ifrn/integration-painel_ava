from typing import Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _

from painel import get_active_themes, get_installed_themes
from painel.models import Ambiente, Popup


def logged_user(request: HttpRequest):
    username = request.session.get("usuario_personificado", getattr(request.user, "username", None))
    if not username:
        return request.user
    User = get_user_model()
    user = User.objects.filter(username=username).first()
    return user if user is not None else request.user


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
