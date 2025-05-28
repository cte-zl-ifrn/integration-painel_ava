# -*- coding: utf-8 -*-
from sc4py.env import env_as_list
from settings.apps import INSTALLED_APPS
from settings.middlewares import MIDDLEWARE
from settings.indebug import DEBUG, TESTING_MODE

# if DEBUG and not TESTING_MODE:
#     try:
#         MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
#         INSTALLED_APPS = env_as_list("DEV_APPS", ["debug_toolbar"]) + INSTALLED_APPS
#         DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: request.get_host() in ["painel"]}
#     except ImportError:
#         print("debug_toolbar not installed, removing from INSTALLED_APPS")

# https://github.com/unbit/django-uwsgi
# https://github.com/giginet/django-debug-toolbar-vcs-info
# https://github.com/orf/django-debug-toolbar-template-timings
# https://github.com/orf/django-debug-toolbar-template-timings
# https://github.com/node13h/django-debug-toolbar-template-profiler
# https://github.com/marceltschoppch/django-requests-debug-toolbar
# https://github.com/djsutho/django-debug-toolbar-request-history
# https://github.com/mikekeda/django-debug-toolbar-line-profiler
# https://github.com/rkern/line_profiler
# https://gitlab.com/living180/pyflame
# https://django-debug-toolbar.readthedocs.io/en/latest/panels.html#uwsgi-stats
