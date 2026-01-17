ARG PYTHON_VERSION=3.14.2-slim-trixie

FROM python:$PYTHON_VERSION AS production

ENV PYTHONUNBUFFERED=1

COPY . /app
WORKDIR /app/src
RUN    useradd -ms /usr/sbin/nologin app \
    && pip install -r /app/requirements.txt  -r /app/requirements-build.txt \
    && mkdir -p /app/static \
    && python manage.py compilescss \
    && python manage.py collectstatic --noinput \
    && ls -l /app/static \
    && pip uninstall -y  -r /app/requirements-build.txt \
    && find /app -type d -name "__pycache__" -exec rm -rf {} + \
    && find /usr/local/lib/python3.14/site-packages/ -type d -name "__pycache__" -exec rm -rf {} +

USER app
EXPOSE 8000
ENTRYPOINT [ "/app/src/django-entrypoint.sh" ]
WORKDIR /app/src
CMD  ["gunicorn" ]


#########################
# Development build stage
########################################################################
FROM production AS development

RUN pip install -r /app/requirements-dev.txt -r /app/requirements-lint.txt -r /app/requirements-build.txt \
    && python manage.py show_urls \
    && find /app -type d -name "__pycache__" -exec rm -rf {} + \
    && find /usr/local/lib/python3.14/site-packages/ -type d -name "__pycache__" -exec rm -rf {} +

USER app
EXPOSE 8000
ENTRYPOINT [ "/app/src/django-entrypoint.sh" ]
WORKDIR /app/src
CMD  ["gunicorn" ]
