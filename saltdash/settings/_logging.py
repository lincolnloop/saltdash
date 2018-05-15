import os
from django.utils.log import DEFAULT_LOGGING

LOGLEVEL = os.getenv("LOGLEVEL", "info").upper()


def _log_format():
    keys = [
        "asctime",
        "created",
        "levelname",
        "levelno",
        "filename",
        "funcName",
        "lineno",
        "module",
        "message",
        "name",
        "pathname",
        "process",
        "processName",
    ]
    return " ".join(["%({0:s})".format(i) for i in keys])


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": _log_format(),
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        }
    },
    "handlers": {
        # console logs to stderr
        "console": {"class": "logging.StreamHandler", "formatter": "default"},
        # Add Handler for Sentry for `warning` and above
        "sentry": {
            "level": "WARNING",
            "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
        },
    },
    "loggers": {
        # default for all undefined Python modules
        "": {"level": "WARNING", "handlers": ["console", "sentry"]},
        # Our application code
        "saltdash": {
            "level": LOGLEVEL,
            "handlers": ["console", "sentry"],
            # Avoid double logging because of root logger
            "propagate": False,
        },
    },
}
if "SYSLOG_IDENTIFIER" in os.environ:
    try:
        from systemd import journal

        LOGGING["formatters"]["default"] = {"format": "%(message)s"}
        LOGGING["handlers"]["console"] = {
            "class": "systemd.journal.JournalHandler",
            "SYSLOG_IDENTIFIER": os.getenv("SYSLOG_IDENTIFIER"),
        }
    except ImportError:
        pass

# Add runserver request logging back in
for k in ["formatters", "handlers", "loggers"]:
    LOGGING[k]["django.server"] = DEFAULT_LOGGING[k]["django.server"]
try:
    # setup pretty logging for local dev
    import readable_log_formatter

    LOGGING["formatters"]["default"] = {
        "()": "readable_log_formatter.ReadableFormatter"
    }
except ImportError:
    pass
