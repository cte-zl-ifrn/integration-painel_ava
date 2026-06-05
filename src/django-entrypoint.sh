#!/usr/bin/env bash

case "${1#-}" in
    gunicorn|python3|python)
        python manage.py migrate
        ;;
esac

exec "$@"
