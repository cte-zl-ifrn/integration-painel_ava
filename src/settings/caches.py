# -*- coding: utf-8 -*-

from sc4py.env import env_as_bool, env_as_int, env_as_list

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env_as_list("DJANGO_CACHES_DEFAULT_LOCATION", "redis://cache:6379/1"),
    }
}

DASHBOARD_CACHE_ENABLED = env_as_bool("DASHBOARD_CACHE_ENABLED", False)
DASHBOARD_CACHE_TIMEOUT = env_as_int("DASHBOARD_CACHE_TIMEOUT", 300)
