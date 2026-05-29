import datetime
import logging

from sc4py.env import env, env_as_bool, env_as_list

logger = logging.getLogger(__name__)

APP_VERSION = "1.0.72"

LAST_STARTUP = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)

SHOW_USERWAY = env_as_bool("SHOW_USERWAY", True)
USERWAY_ACCOUNT = env("USERWAY_ACCOUNT", None)
SHOW_VLIBRAS = env_as_bool("SHOW_VLIBRAS", True)
SHOW_SUPPORT_FORM = env_as_bool("SHOW_SUPPORT_FORM", True)
SHOW_SUPPORT_CHAT = env_as_bool("SHOW_SUPPORT_CHAT", True)
HOSTNAME = env("HOSTNAME", "-")


# Apps
MY_APPS = env_as_list(
    "MY_APPS",
    [
        "theme_ifrn23",
        "theme_ifrn25",
        "backup",
        "painel",
        "health",
        "base",
    ],
)

THIRD_APPS = env_as_list(
    "THIRD_APPS",
    [
        "import_export",
        "simple_history",
        "safedelete",
        "admin_auto_filters",
        "django_extensions",
        "sass_processor",
    ],
)

try:
    import django_extensions  # noqa F401
except ImportError:
    logger.warning("django_extensions not installed, removing from INSTALLED_APPS")
    THIRD_APPS.remove("django_extensions")

try:
    import sass_processor  # noqa F401
except ImportError:
    logger.warning("sass_processor NOT INSTALLED, removing from INSTALLED_APPS")
    THIRD_APPS.remove("sass_processor")

DJANGO_APPS = env_as_list(
    "DJANGO_APPS",
    [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ],
)
HACK_APPS = env_as_list(
    "HACK_APPS",
    ["a4"],
)
INSTALLED_APPS = MY_APPS + THIRD_APPS + DJANGO_APPS + HACK_APPS


SITE_ID = 1
