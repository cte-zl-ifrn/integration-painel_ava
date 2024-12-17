#!/usr/bin/env bash

case "${1#-}" in
    gunicorn|python)
        python manage.py migrate
        exec $@
        ;;
    *)
        exec $@
        ;;
esac

