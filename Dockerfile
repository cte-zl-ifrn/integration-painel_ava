FROM python:3.13.1-slim-bookworm

ENV PYTHONUNBUFFERED 1
ARG EXTRA_REQ="-r /requirements-dev.txt -r /requirements-lint.txt"

RUN apt-get update \
    && apt-get -y install curl vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements*.txt /
COPY docker/django-entrypoint.sh /django-entrypoint.sh
COPY src /apps/app
WORKDIR /apps/app
RUN pip install --upgrade --no-cache-dir --root-user-action ignore pip \
    && pip install --root-user-action ignore -r /requirements.txt $EXTRA_REQ \
    && mkdir -p /var/static \
    && echo '__version__ = "unknown"' > /usr/local/lib/python3.13/site-packages/django_better_choices/version.py \
    && python manage.py compilescss \
    && python manage.py collectstatic --noinput

EXPOSE 80
ENTRYPOINT [ "/django-entrypoint.sh" ]
WORKDIR /apps/app
CMD  ["gunicorn"]
