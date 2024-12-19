from sc4py.env import env, env_as_list, env_as_bool
import datetime

APP_VERSION = "1.1.13"

LAST_STARTUP = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)

SHOW_USERWAY = env_as_bool("SHOW_USERWAY", True)
USERWAY_ACCOUNT = env("USERWAY_ACCOUNT", None)
SHOW_VLIBRAS = env_as_bool("SHOW_VLIBRAS", True)
SHOW_SUPPORT_FORM = env_as_bool("SHOW_SUPPORT_FORM", True)
SHOW_SUPPORT_CHAT = env_as_bool("SHOW_SUPPORT_CHAT", True)


# Apps
MY_APPS = env_as_list(
    "MY_APPS",
    [
        "painel",
        "health",
        "base",
    ],
)
THIRD_APPS = env_as_list(
    "THIRD_APPS",
    [
        # 'markdownx',
        "django_extensions",
        "import_export",
        "simple_history",
        "safedelete",
        "sass_processor",
        "djrichtextfield",
        "django_json_widget",
        # "django_admin_json_editor",
        # "corsheaders",
        "adminlte3",
        # "adminlte3/admin",
    ],
)

DJANGO_APPS = env_as_list(
    "DJANGO_APPS",
    [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        # "django.contrib.staticfiles",
        "a4",
    ],
)
HACK_APPS = env_as_list(
    "HACK_APPS",
    [
        # "suaplogin",
    ],
)
INSTALLED_APPS = MY_APPS + THIRD_APPS + DJANGO_APPS + HACK_APPS
