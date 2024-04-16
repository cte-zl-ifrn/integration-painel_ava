#!/usr/bin/env python
import os
import sys
from settings import DATABASES, DEBUG
import psycopg
import time
import logging


def _wait_db(db):
    connection = psycopg.connect(
        dbname=db["NAME"],
        user=db["USER"],
        password=db["PASSWORD"],
        host=db["HOST"],
        port=db["PORT"],
    )
    while connection.closed:
        logging.info(f"ERROR: Aguardando o banco {db['HOST']:db['PORT']/db['NAME']} subir")
        time.sleep(3)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("ops!") from exc

    if len(sys.argv) > 1 and sys.argv[1] in ["runserver", "runserver_plus"]:
        _wait_db(DATABASES["default"])
        execute_from_command_line([sys.argv[0], "collectstatic", "--noinput"])
        execute_from_command_line([sys.argv[0], "migrate"])

        from sc4py.env import env_as_bool

        if env_as_bool("DJANGO_DEBUG", False):
            try:
                import debugpy

                debugpy.listen(("0.0.0.0", 5678))
                # debugpy.wait_for_client()
            except Exception:
                pass
            # debugpy.breakpoint()

    execute_from_command_line(sys.argv)
