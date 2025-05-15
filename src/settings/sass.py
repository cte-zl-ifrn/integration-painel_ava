# -*- coding: utf-8 -*-
import pathlib
from settings.developments import DEBUG

PROJECT_PATH = pathlib.Path(__file__).parent.parent.resolve()

SASS_PROCESSOR_AUTO_INCLUDE = True
SASS_PROCESSOR_INCLUDE_FILE_PATTERN = r"^.+\.scss$"
SASS_PRECISION = 8
SASS_OUTPUT_STYLE = "nested" if DEBUG else "compressed"
SASS_PROCESSOR_INCLUDE_DIRS = [PROJECT_PATH / "theme_ifrn23/static/theme/ifrn23/scss/"]
