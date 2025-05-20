import os
from django.core.wsgi import get_wsgi_application
from settings.indebug import DEBUG

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
application = get_wsgi_application()

if not DEBUG:
    from whitenoise import WhiteNoise

    application = WhiteNoise(application())
