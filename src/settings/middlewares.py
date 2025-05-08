# -*- coding: utf-8 -*-
# Middleware
MIDDLEWARE = [
    "painel.middleware.ExceptionMiddleware",
    "painel.middleware.GoToHTTPSMiddleware",  # <-
    "painel.middleware.XForwardedForMiddleware",
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
