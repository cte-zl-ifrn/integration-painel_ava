# -*- coding: utf-8 -*-
from sc4py.env import env

# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": env("POSTGRES_ENGINE", "django.db.backends.postgresql"),
        "HOST": env("POSTGRES_HOST", "db"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "NAME": env("POSTGRES_DATABASE", "painel"),
        "USER": env("POSTGRES_USER", "ava_user"),
        "PASSWORD": env("POSTGRES_PASSWORD", "ava_pass"),
        "OPTIONS": {"options": env("POSTGRES_OPTIONS", "")},
    }
}

# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
