from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("-/", include("saltdash.healtcheck.urls")),
    path("admin/", admin.site.urls),
    path(
        "{}/".format(settings.SOCIAL_AUTH_URL_PREFIX),
        include("social_django.urls", namespace="social"),
    ),
    path("", include("saltdash.dash.urls")),
]
