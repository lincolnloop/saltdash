import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saltdash.settings")


def manage():
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
