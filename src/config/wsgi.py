"""WSGI config for the project."""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
