# -*- coding: utf-8 -*-
from sc4py.env import env, env_as_int, env_as_bool, env_as_list

EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_FILE_PATH = env("DJANGO_EMAIL_FILE_PATH", None)
EMAIL_HOST = env("DJANGO_EMAIL_HOST", "mail")
EMAIL_PORT = env_as_int("DJANGO_EMAIL_PORT", 1025)
EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", "")
EMAIL_USE_LOCALTIME = env_as_bool("DJANGO_EMAIL_USE_LOCALTIME", False)
EMAIL_USE_TLS = env_as_bool("DJANGO_EMAIL_USE_TLS", False)
EMAIL_USE_SSL = env_as_bool("DJANGO_EMAIL_USE_SSL", False)
EMAIL_SSL_CERTFILE = env("DJANGO_EMAIL_SUBJECT_PREFIX", None)
EMAIL_SSL_KEYFILE = env("DJANGO_EMAIL_SSL_KEYFILE", None)
EMAIL_TIMEOUT = env_as_bool("DJANGO_EMAIL_TIMEOUT¶", None)
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", "Atendimento do SUAP-Login <cte.ead@ifrn.edu.br>")
DEFAULT_REPLYTO_EMAIL = env_as_list("DEFAULT_REPLYTO_EMAIL", ["Atendimento do SUAP-Login <cte.ead@ifrn.edu.br>"])
