# -*- coding: utf-8 -*-

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "painel.context_processors.popup",
                "painel.context_processors.layout_settings",
                "painel.context_processors.top_menu",
            ]
        },
    },
]
