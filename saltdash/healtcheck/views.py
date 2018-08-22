import logging

from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import connection
from django.http import HttpResponse, JsonResponse

log = logging.getLogger(__name__)


def alive(request):
    return HttpResponse("ok")


def healthcheck(request):
    # Verify DB is connected
    errors = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
    except Exception:
        log.exception("Database connection failed.")
        errors.append("Database error")
    # Verify static files are reachable
    filename = "app.css"
    if not staticfiles_storage.exists(filename):
        log.error("Can't find %s in static files.", filename)
        errors.append("Static files error.")
    if errors:
        return JsonResponse({"healthy": False, "errors": errors}, status=503)
    else:
        return JsonResponse({"healthy": True})
