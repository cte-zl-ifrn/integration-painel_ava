#!/usr/bin/env python
import os
import sys
from sc4py.env import env
import psycopg
import time
import logging
from settings.indebug import DEBUG, TESTING_MODE  # noqa: F401
from settings.databases import DATABASES  # noqa: F401


def _wait_db():
    db = DATABASES['default']
    host = db["HOST"]
    port = db["PORT"]
    dbname = db["NAME"]
    user = db["USER"]
    password = db["PASSWORD"]

    connection = psycopg.connect(host=host, port=port, dbname=dbname, user=user, password=password)

    while connection.closed:
        logging.info(f"ERROR: Aguardando o banco {host}:{port}/{dbname} subir")
        time.sleep(3)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("ops!") from exc

    if len(sys.argv) > 1 and sys.argv[1] in ["runserver", "runserver_plus"]:
        _wait_db()
        # execute_from_command_line([sys.argv[0], "collectstatic", "--noinput"])
        execute_from_command_line([sys.argv[0], "migrate"])

        if DEBUG:
            try:
                import debugpy

                debugpy.listen(("0.0.0.0", 5678))
                # debugpy.wait_for_client()
            except Exception:
                pass
            # debugpy.breakpoint()

    execute_from_command_line(sys.argv)
