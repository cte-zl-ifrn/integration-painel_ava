from sc4py.env import env_as_int

DEFAULT_HTTP_TIMEOUT =  env_as_int('DJANGO_DEFAULT_HTTP_TIMEOUT', 5)