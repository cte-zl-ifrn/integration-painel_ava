# -*- coding: utf-8 -*-
from sc4py.env import env, env_as_bool, env_as_list

ALLOWED_HOSTS = env_as_list("DJANGO_ALLOWED_HOSTS", ["painel"] if env_as_bool("DJANGO_DEBUG", True) else [])
WSGI_APPLICATION = env("DJANGO_WSGI_APPLICATION", "wsgi.application")
USE_X_FORWARDED_HOST = env_as_bool("DJANGO_USE_X_FORWARDED_HOST", True)
SECURE_PROXY_SSL_HEADER = env_as_list("DJANGO_SECURE_PROXY_SSL_HEADER", "")
ROOT_URL_PATH = env("DJANGO_ROOT_URL_PATH", "painel")
ROOT_URLCONF = env("DJANGO_ROOT_URLCONF", "urls")
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = env("DJANGO_STATIC_URL", f"{ROOT_URL_PATH}/static/")
STATIC_ROOT = env("DJANGO_STATIC_ROOT", "/var/static")
MEDIA_URL = env("DJANGO_MEDIA_URL", f"{ROOT_URL_PATH}/media/")
MEDIA_ROOT = env("DJANGO_MEDIA_ROOT", "/var/media")
MARKDOWNX_URLS_PATH = env("MARKDOWNX_URLS_PATH", "{ROOT_URL_PATH}/markdownx/markdownify/")
MARKDOWNX_UPLOAD_URLS_PATH = env("MARKDOWNX_UPLOAD_URLS_PATH", "{ROOT_URL_PATH}/markdownx/upload/")
