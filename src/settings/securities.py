# -*- coding: utf-8 -*-
from sc4py.env import env, env_as_bool, env_as_list, env_as_int

# from corsheaders.signals import check_request_enabled


# def cors_allow_mysites(sender, request, **kwargs):
#     return False
#     return MySite.objects.filter(host=request.headers["origin"]).exists()
# check_request_enabled.connect(cors_allow_mysites)


SECRET_KEY = env("DJANGO_SECRET_KEY", "changeme")
LOGIN_URL = env("DJANGO_LOGIN_URL", "http://painel/login/")
LOGIN_REDIRECT_URL = env("DJANGO_LOGIN_REDIRECT_URL", "http://painel/")
LOGOUT_REDIRECT_URL = env("DJANGO_LOGOUT_REDIRECT_URL", "http://login/logout/")
AUTH_USER_MODEL = env("DJANGO_AUTH_USER_MODEL", "a4.Usuario")
AUTHENTICATION_BACKENDS = env_as_list("vAUTHENTICATION_BACKENDS", ["django.contrib.auth.backends.ModelBackend"])
AUTH_PASSWORD_VALIDATORS = env_as_list("DJANGO_AUTH_PASSWORD_VALIDATORS", [])


CORS_ALLOWED_ORIGINS = env_as_list("DJANGO_CORS_ALLOWED_ORIGINS", ["sameorigin"])
# CORS_ALLOWED_ORIGIN_REGEXES = env_as_list("DJANGO_CORS_ALLOWED_ORIGIN_REGEXES", [])
# CORS_ALLOW_ALL_ORIGINS = env_as_bool("DJANGO_CORS_ALLOW_ALL_ORIGINS", False)
# CORS_URLS_REGEX = env_as_list("DJANGO_CORS_URLS_REGEX", r"^.*$")
# CORS_ALLOW_METHODS = env_as_list("DJANGO_CORS_ALLOW_METHODS", ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"])
# CORS_ALLOW_HEADERS = env_as_list("DJANGO_CORS_ALLOW_HEADERS", ["content-type", "user-agent"])
# CORS_EXPOSE_HEADERS = env_as_list("DJANGO_CORS_EXPOSE_HEADERS", [])
# CORS_PREFLIGHT_MAX_AGE = env_as_int("DJANGO_CORS_PREFLIGHT_MAX_AGE", 86400)
# CORS_ALLOW_CREDENTIALS = env_as_bool("DJANGO_CORS_ALLOW_CREDENTIALS", False)
# CORS_ALLOW_PRIVATE_NETWORK = env_as_bool("DJANGO_CORS_ALLOW_PRIVATE_NETWORK", False)


CSRF_COOKIE_AGE = env_as_int("DJANGO_CSRF_COOKIE_AGE", 60 * 60 * 24 * 365)
CSRF_COOKIE_DOMAIN = env("DJANGO_CSRF_COOKIE_DOMAIN", None)
CSRF_COOKIE_HTTPONLY = env_as_bool("DJANGO_CSRF_COOKIE_HTTPONLY", False)
CSRF_COOKIE_NAME = env("DJANGO_CSRF_COOKIE_NAME", "csrftoken")
CSRF_COOKIE_PATH = env("DJANGO_CSRF_COOKIE_PATH", "/")
CSRF_COOKIE_SAMESITE = env("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SECURE = env_as_bool("DJANGO_CSRF_COOKIE_SECURE", False)
CSRF_USE_SESSIONS = env_as_bool("DJANGO_CSRF_USE_SESSIONS", False)
CSRF_FAILURE_VIEW = env("DJANGO_CSRF_FAILURE_VIEW", "django.views.csrf.csrf_failure")
CSRF_HEADER_NAME = env("DJANGO_CSRF_HEADER_NAME", "HTTP_X_CSRFTOKEN")
CSRF_TRUSTED_ORIGINS = env_as_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])


OAUTH = {
    "BASE_URL": env("OAUTH_BASE_URL", "http://login"),
    "REDIRECT_URI": env("OAUTH_REDIRECT_URI", "http://painel/authenticate/"),
    "CLIENT_ID": env("OAUTH_CLIENT_ID", "changeme"),
    "CLIENT_SECRET": env("OAUTH_CLIENT_SECRET", "changeme"),
    "VERIFY_SSL": env_as_bool("OAUTH_VERIFY_SSL", False),
    "TOKEN_URL": env("OAUTH_TOKEN_URL", "http://login/o/token/"),
    "USERINFO_URL": env("OAUTH_USERINFO_URL", "http://login/api/v1/userinfo/"),
}

SUAP_INTEGRADOR_KEY = env("SUAP_INTEGRADOR_KEY", "changeme")
