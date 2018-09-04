import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Func, Value
from django.utils import timezone as tz
from saltdash.dash import models


class Command(BaseCommand):
    help = "Removes items from job cache database older than X days"

    def add_arguments(self, parser):
        parser.add_argument(
            "days", type=int, help="Delete job cache items older than this many days"
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            dest="no_input",
            help="Don't ask for confirmation prior to deleting items",
        )

    def handle(self, *args, **options):
        days = options["days"]
        if days < 1:
            raise CommandError(
                "Not purging because less than 1 day specified. "
                "Days = {}".format(days)
            )
        before = tz.now() - datetime.timedelta(days=days)

        results = models.Result.objects.filter(completed__lt=before)
        jobs = models.Job.objects.annotate(
            date=Func(F("jid"), Value("YYYYMMDDHH24MISSMS"), function="TO_TIMESTAMP")
        ).filter(date__lt=before)
        self.stdout.write(
            self.style.WARNING(
                "Deleting {} jobs and {} results created before {}.".format(
                    jobs.count(), results.count(), before
                )
            )
        )

        if not options["no_input"]:
            response = input("Are you sure you want to delete these items? [y/N]")
            if response.lower() not in ["y", "yes"]:
                self.stdout.write("Nothing deleted.")
                return
        results.delete()
        jobs.delete()
        self.stdout.write("Job cache purged.")
