import sys

from django.conf import settings
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Warm-up wsgi app on import
warmup = application(
    {
        "REQUEST_METHOD": "GET",
        "SERVER_NAME": "127.0.0.1",
        "SERVER_PORT": 80,
        "PATH_INFO": "/-/alive/",
        "wsgi.input": sys.stdin,
    },
    lambda x, y: None,
)
