# -*- coding: utf-8 -*-
from sc4py.env import env
import logging.config
from .apps import INSTALLED_APPS

# Get loglevel from env
LOGLEVEL = env("DJANGO_LOGLEVEL", "DEBUG").upper()


class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYANO = "\033[96m"
    STRONG = "\033[1m"
    UNDERLINE = "\033[4m"
    NONE = "\033[0m"


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "datefmt": "[%X]",
        "formatters": {
            "longformat": {
                # "format": f"{Color.GREEN}%(asctime)s {Color.YELLOW}%(levelname)s {Color.MAGENTA}%(name)s:%(lineno)s {Color.CYANO}pid:%(process)d {Color.NONE}%(message)s"  # noqa
                "format": f"%(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "rich.logging.RichHandler",
                "formatter": "longformat",
            },
        },
        "loggers": dict(
            **{"": {"level": "INFO", "handlers": ["console"]}},
            **{app: {"level": LOGLEVEL} for app in INSTALLED_APPS},
        ),
    }
)
