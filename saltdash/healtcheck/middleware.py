def healthcheck_bypass_host_check(get_response):
    def middleware(request):
        if request.path.startswith("/-/"):
            request.get_host = lambda: request._get_raw_host()

        return get_response(request)

    return middleware
