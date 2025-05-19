#!/usr/bin/env python
import os
import sys
from sc4py.env import env, env_as_bool
import psycopg
import time
import logging


def _wait_db():
    host = env("POSTGRES_HOST", "db")
    port = env("POSTGRES_PORT", "5432")
    dbname = env("POSTGRES_DATABASE", "painel")
    user = env("POSTGRES_USER", "ava_user")
    password = env("POSTGRES_PASSWORD", "ava_pass")

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
