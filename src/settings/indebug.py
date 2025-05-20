# -*- coding: utf-8 -*-
import sys
from sc4py.env import env_as_bool

DEBUG = env_as_bool("DJANGO_DEBUG", True)
TESTING_MODE = "test" in sys.argv
