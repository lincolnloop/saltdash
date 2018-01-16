import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saltdash.settings.local")

from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application


def manage():
    execute_from_command_line(sys.argv)

application = get_wsgi_application()
