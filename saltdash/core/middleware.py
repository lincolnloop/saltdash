import logging
from re import compile

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import is_safe_url

log = logging.getLogger(__name__)

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip("/"))] + [
    compile(expr) for expr in getattr(settings, "LOGIN_EXEMPT_URLS", [])
]

# https://gist.github.com/agusmakmun/b71ac536124e0535a8b076989f8cfcd3
class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before the view is called
        if not request.user.is_authenticated:
            path = request.path_info.lstrip("/")
            if not any(m.match(path) for m in EXEMPT_URLS):
                redirect_to = settings.LOGIN_URL
                # Add 'next' GET variable to support redirection after login
                if len(path) > 0 and is_safe_url(
                    url=request.path_info, allowed_hosts={request.get_host()}
                ):
                    redirect_to = "{}?next={}".format(
                        settings.LOGIN_URL, request.path_info
                    )
                return HttpResponseRedirect(redirect_to)
        response = self.get_response(request)
        # After the view is called
        return response
