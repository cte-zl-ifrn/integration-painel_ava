# -*- coding: utf-8 -*-
from sc4py.env import env, env_as_bool, env_as_list

ALLOWED_HOSTS = env_as_list("DJANGO_ALLOWED_HOSTS", ["painel"] if env_as_bool("DJANGO_DEBUG", True) else [])
WSGI_APPLICATION = env("DJANGO_WSGI_APPLICATION", "wsgi.application")
USE_X_FORWARDED_HOST = env_as_bool("DJANGO_USE_X_FORWARDED_HOST", True)
SECURE_PROXY_SSL_HEADER = env_as_list("DJANGO_SECURE_PROXY_SSL_HEADER", "")
ROOT_URL_PATH = env("DJANGO_ROOT_URL_PATH", "")
ROOT_URLCONF = env("DJANGO_ROOT_URLCONF", "urls")
MEDIA_URL = env("DJANGO_MEDIA_URL", f"{ROOT_URL_PATH}/media/")
MEDIA_ROOT = env("DJANGO_MEDIA_ROOT", "/app/media")
MARKDOWNX_URLS_PATH = env("MARKDOWNX_URLS_PATH", "{ROOT_URL_PATH}/markdownx/markdownify/")
MARKDOWNX_UPLOAD_URLS_PATH = env("MARKDOWNX_UPLOAD_URLS_PATH", "{ROOT_URL_PATH}/markdownx/upload/")

STATIC_URL = env("DJANGO_STATIC_URL", f"static/")
STATIC_ROOT = env("DJANGO_STATIC_ROOT", "/app/static")
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"  # Configuração para otimizar arquivos estáticos
)
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]
