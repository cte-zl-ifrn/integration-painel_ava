import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.wsgi import get_wsgi_application
from settings.indebug import DEBUG
from whitenoise import WhiteNoise

application = WhiteNoise(get_wsgi_application()) if not DEBUG else get_wsgi_application()
