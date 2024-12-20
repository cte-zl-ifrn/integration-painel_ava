# -*- coding: utf-8 -*-
from sc4py.env import env_as_bool
from django.core.handlers import exception
from debug_toolbar import middleware

# Middleware
MIDDLEWARE = [
    "painel.middleware.ExceptionMiddleware",
    "painel.middleware.GoToHTTPSMiddleware",  # <-
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "painel.middleware.AuthMobileUserMiddleware",
    # "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]
