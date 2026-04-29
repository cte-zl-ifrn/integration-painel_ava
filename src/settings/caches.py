# -*- coding: utf-8 -*-

from sc4py.env import env, env_as_int, env_as_list, env_as_bool

CACHES = {
    "default": {
        "BACKEND": env("DJANGO_CACHES_DEFAULT_BACKEND", "django.core.cache.backends.redis.RedisCache"),
        "LOCATION": env_as_list("DJANGO_CACHES_DEFAULT_LOCATION", "redis://cache:6379/1"),
    }
}

DASHBOARD_CACHE_ENABLED = env_as_bool("DASHBOARD_CACHE_ENABLED", True)
DASHBOARD_CACHE_TIMEOUT = env_as_int('DASHBOARD_CACHE_TIMEOUT', 300)