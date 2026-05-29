ARG BASEIMAGE=6.0.5.32

#########################
# 1. Base stage
########################################################################
FROM ctezlifrn/avaintegrationbase:$BASEIMAGE AS base

RUN uv pip uninstall --system dsgovbr || true

#########################
# 2. Development stage
########################################################################
FROM base AS development

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ make \
    && uv pip install --system \
        black ruff doc8 pytest pytest-cov python-dotenv pytest-coverage-gate pytest-django \
        Werkzeug django-debug-toolbar debugpy \
        libsass django-compressor django-sass-processor \
    && apt-get purge -y --auto-remove gcc g++ make \
    && rm -rf /var/lib/apt/lists/*

COPY src /app/src
WORKDIR /app/src

RUN mkdir -p /app/static \
    && python manage.py compilescss \
    && python manage.py collectstatic --noinput \
    && ls -l /app/static \
    && find /app -type d -name "__pycache__" -exec rm -rf {} + \
    && find /usr/local/lib/python3.14/site-packages/ -type d -name "__pycache__" -exec rm -rf {} +

USER app
EXPOSE 8000
CMD  ["python", "manage.py", "runserver_plus", "0.0.0.0:8000"]


#########################
# 3. Production stage
########################################################################
FROM base AS production

COPY --chown=root:app --from=development /app /app

USER app
EXPOSE 8000
WORKDIR /app/src
CMD  ["gunicorn"]