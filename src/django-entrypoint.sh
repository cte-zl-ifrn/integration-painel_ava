#!/usr/bin/env bash

case "${1#-}" in
    /app/venv/bin/gunicorn|/app/venv/bin/python3|/app/venv/bin/python)
        /app/venv/bin/python3 manage.py show_urls
        /app/venv/bin/python3 manage.py migrate
        ;;
esac

exec "$@"
