# # -*- coding: utf-8 -*-
import logging
import sentry_sdk
from sc4py.env import env, env_as_bool, env_as_int
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from django.core.exceptions import DisallowedHost
from .apps import APP_VERSION

if env("SENTRY_DNS", None):
    sentry_sdk.init(
        dsn=env("SENTRY_DNS"),
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.INFO),
        ],
        default_integrations=env_as_bool("SENTRY_DEFAULT_INTEGRATIONS", True),
        # Informe em porcentual, ou seja, 50 significa que 100% de erros serão reportados.
        sample_rate=env_as_int("SENTRY_SAMPLE_RATE", 100) / 100.0,
        # before_send=,
        # before_breadcrumb=,
        # Informe em porcentual, ou seja, 50 significa que 100% de erros serão reportados.
        traces_sample_rate=env_as_int("SENTRY_TRACES_SAMPLE_RATE", 100) / 100.0,
        # traces_sampler=
        # If you wish to associate users to errors (assuming you are using django.contrib.auth) you may enable sending PII data.
        send_default_pii=env_as_bool("SENTRY_SEND_DEFAULT_PII", True),
        debug=env_as_bool("SENTRY_DEBUG", False),
        environment=env("SENTRY_ENVIRONMENT", "local"),
        max_breadcrumbs=env_as_int("SENTRY_MAX_BREADCRUMBS", 100),
        with_locals=env_as_bool("SENTRY_WITH_LOCALS", True),
        ignore_errors=[DisallowedHost],
        # release=env('SENTRY_RELEASE', '1.0.0'),
        # attach_stacktrace=env('SENTRY_ATTACH_STACKTRACE', 'off'),
        # server_name=env('SENTRY_SERVER_NAME', 'off'),
        # in_app_include=env_as_list('SENTRY_IN_APP_INCLUDE', []),
        # in_app_exclude=env_as_list('SENTRY_IN_APP_EXCLUDE', []),
        # request_bodies=env_as_list('SENTRY_REQUEST_BODIES', []),
        # ca_certs=
        # request_bodies=
        # send_client_reports=
        # transport=,
        # shutdown_timeout=env_as_int('SENTRY_SHUTDOWN_TIMEOUT', 2),
    )
