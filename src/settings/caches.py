# -*- coding: utf-8 -*-

from sc4py.env import env, env_as_list


CACHES = {
    "default": {
        "BACKEND": env("DJANGO_CACHES_DEFAULT_BACKEND", "django_valkey.cache.ValkeyCache"),
        "LOCATION": env_as_list("DJANGO_CACHES_DEFAULT_LOCATION", ["valkey://cache:6379/0"]),
    }
}
