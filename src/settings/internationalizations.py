# -*- coding: utf-8 -*-
from pathlib import Path
from sc4py.env import env, env_as_bool

# https://docs.djangoproject.com/en/5.0/topics/i18n/


LANGUAGE_CODE = env("DJANGO_USE_I18N", "pt-br")
TIME_ZONE = env("DJANGO_USE_I18N", "America/Fortaleza")
USE_I18N = env_as_bool("DJANGO_USE_I18N", True)
USE_TZ = env_as_bool("DJANGO_USE_TZ", True)
