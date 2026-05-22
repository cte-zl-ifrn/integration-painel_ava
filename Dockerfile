ARG BASEIMAGE=6.0.5.32


#########################
# Development stage
########################################################################
FROM ctezlifrn/avaintegrationbase:$BASEIMAGE AS development

RUN uv pip uninstall --system dsgovbr
RUN uv pip install --system \
                    django-safedelete libsass django-compressor django-ninja PyJWT \
                    black ruff doc8 pytest pytest-cov python-dotenv pytest-coverage-gate pytest-django \
                    django-sass-processor Werkzeug django-debug-toolbar

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
WORKDIR /app/src
CMD  ["python", "manage.py", "runserver_plus", "0.0.0.0:8000"]



#########################
# Production stage
########################################################################
FROM ctezlifrn/avaintegrationbase:$BASEIMAGE AS production

COPY --chown=root:app --from=development /app /app

USER app
EXPOSE 8000
WORKDIR /app/src
CMD  ["gunicorn" ]
