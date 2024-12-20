FROM python:3.13.1-slim-bookworm

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install curl vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /

RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r /requirements.txt

COPY requirements-dev.txt /apps/req/requirements-dev.txt
WORKDIR /apps/req

RUN pip install --no-cache-dir -r requirements-dev.txt

# FIX: bug on corsheaders
# RUN echo 'import django.dispatch;check_request_enabled = django.dispatch.Signal()' > /usr/local/lib/python3.10/site-packages/corsheaders/signals.py

COPY docker/django-entrypoint.sh /django-entrypoint.sh
COPY src /apps/app
WORKDIR /apps/app
RUN python manage.py compilescss && \
    python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT [ "/django-entrypoint.sh" ]
WORKDIR /apps/app
CMD  ["gunicorn"]
