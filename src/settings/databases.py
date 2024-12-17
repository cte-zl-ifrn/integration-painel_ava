# -*- coding: utf-8 -*-
from sc4py.env import env, env_as_int

# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": env("POSTGRES_ENGINE", "django.db.backends.postgresql"),
        "HOST": env("POSTGRES_HOST", "db"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "NAME": env("POSTGRES_DATABASE", "painel"),
        "USER": env("POSTGRES_USER", "ava_user"),
        "PASSWORD": env("POSTGRES_PASSWORD", "ava_pass"),
        "OPTIONS": {
            "options": env("POSTGRES_OPTIONS", ""),
            "autocommit": False,
            "pool": {
                "min_size": env_as_int("DEFAULT_POOL_MIN_SIZE", 1),
                "max_size": env_as_int("DEFAULT_POOL_MAX_SIZE", 100),
                # "open": env_as_bool("DEFAULT_POOL_OPEN", True),
                "name": env("DEFAULT_POOL_NAME", ""),
                "timeout": env_as_int("DEFAULT_POOL_TIMEOUT", 1),
                "max_lifetime": env_as_int("DEFAULT_POOL_MAX_LIFETIME", 1200),
                "max_idle": env_as_int("DEFAULT_POOL_MAX_IDLE", 600),
                "reconnect_timeout": env_as_int("DEFAULT_POOL_RECONNECT_TIMEOUT", 300),
                "num_workers": env_as_int("DEFAULT_POOL_NUM_WORKERS", 3),
            }
        },
    }
}

# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
