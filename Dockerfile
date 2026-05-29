ARG BASEIMAGE=6.0.5.32

#########################
# 1. Base stage
########################################################################
FROM ctezlifrn/avaintegrationbase:$BASEIMAGE AS build

COPY --chown=root:app src /app/src

WORKDIR /app/src

RUN uv pip install --system \
        django-compressor django-sass-processor

RUN python manage.py collectstatic --noinput -v 0 \
    && find /app/static -type d -name "__pycache__" -exec rm -rf {} + \
    && find /usr/local/lib/python3.14/site-packages/ -type d -name "__pycache__" -exec rm -rf {} + \
    && ls -l /app/static


#########################
# 2. Production stage
########################################################################
FROM ctezlifrn/avaintegrationbase:$BASEIMAGE AS production

COPY --chown=root:app --from=build /app /app

USER app
EXPOSE 8000
WORKDIR /app/src
CMD  ["gunicorn"]


#########################
# 3. Development stage
########################################################################
FROM ctezlifrn/avaintegrationbase:$BASEIMAGE AS development

RUN uv pip install --system \
        django-compressor django-sass-processor \
        black ruff doc8 pytest pytest-cov python-dotenv pytest-coverage-gate pytest-django \
        Werkzeug django-debug-toolbar debugpy

USER app
EXPOSE 8000
CMD  ["python", "manage.py", "runserver_plus", "0.0.0.0:8000"]
