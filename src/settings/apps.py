from sc4py.env import env, env_as_list, env_as_bool
import datetime

APP_VERSION = "1.2.1"

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
        "painel",
        "health",
        "base",
    ],
)
THIRD_APPS = env_as_list(
    "THIRD_APPS",
    [
        "django_extensions",
        "import_export",
        "simple_history",
        "safedelete",
        "sass_processor",
        # "adminlte3",
        # "adminlte3/admin",
    ],
)

try:
    import django_extensions
except ImportError:
    print("django_extensions not installed, removing from INSTALLED_APPS")
    THIRD_APPS.remove("django_extensions")


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
    [
        "a4",
    ],
)
INSTALLED_APPS = MY_APPS + THIRD_APPS + DJANGO_APPS + HACK_APPS


SITE_ID = 1
