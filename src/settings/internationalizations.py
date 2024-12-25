# -*- coding: utf-8 -*-
from pathlib import Path
from sc4py.env import env, env_as_bool

# https://docs.djangoproject.com/en/5.0/topics/i18n/


LANGUAGE_CODE = env("DJANGO_USE_I18N", "pt-br")
TIME_ZONE = env("DJANGO_USE_I18N", "America/Fortaleza")
USE_I18N = env_as_bool("DJANGO_USE_I18N", True)
USE_TZ = env_as_bool("DJANGO_USE_TZ", True)

DJRICHTEXTFIELD_CONFIG = {
    # 'js': ['//cdn.tiny.cloud/1/j032qwayos8732iz4nwlj992jg4u08la2e80ewiwiqxraz2d/tinymce/7/tinymce.min.js'],
    'js': ['https://cdn.tiny.cloud/1/j032qwayos8732iz4nwlj992jg4u08la2e80ewiwiqxraz2d/tinymce/5/tinymce.min.js'],
    'init_template': 'djrichtextfield/init/tinymce.js',
    'settings': {
        'menubar': False,
        'plugins': 'link image',
        'toolbar': 'bold italic | link image | removeformat',
        'width': 700
    }
}
