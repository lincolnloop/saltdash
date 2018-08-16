from django.core.management import BaseCommand
from saltdash.core import server


class Command(BaseCommand):
    help = "Start Saltdash webserver"

    def handle(self, *args, **options):
        server.start()
