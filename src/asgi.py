import os
from django.core.asgi import get_asgi_application
from settings.indebug import DEBUG

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
application = get_asgi_application()

if not DEBUG:
    from whitenoise import WhiteNoise

    application = WhiteNoise(application)
