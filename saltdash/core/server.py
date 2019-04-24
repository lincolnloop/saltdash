import codecs
import logging
import os
import socket
import time
from urllib.parse import quote

import waitress

from .. import config, wsgi

log = logging.getLogger(__name__)


class NonBindingServer(waitress.server.UnixWSGIServer):
    """
    Bypass binding to the socket.
    In the case of Systemd sockets, it is already bound.
    """

    def bind_server_socket(self):
        pass


def systemd_notify(msg):
    """
    Allow app to be setup as `Type=notify` in systemd
    Sending signals when it is ready to start serving.
    """
    if "NOTIFY_SOCKET" not in os.environ:
        log.debug("No systemd NOTIFY_SOCKET set")
        return
    msg = codecs.latin_1_encode(msg)[0]
    addr = os.environ["NOTIFY_SOCKET"]
    if addr[0] == "@":
        addr = "\0" + addr[1:]
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        sock.connect(addr)
        sock.sendall(msg)
    except:
        log.exception("Could not notify systemd")


def start():
    """Start webserver"""
    logged_app = TransLogger(wsgi.application)
    # Work with systemd socket activation
    if "LISTEN_FDNAMES" in os.environ and not config.LISTEN:
        wsgi_server = NonBindingServer(
            logged_app, _sock=socket.fromfd(3, socket.AF_UNIX, socket.SOCK_STREAM)
        )
    elif config.LISTEN.startswith("/"):
        wsgi_server = waitress.server.create_server(
            logged_app, unix_socket=config.LISTEN
        )
    elif config.LISTEN:
        wsgi_server = waitress.server.create_server(logged_app, listen=config.LISTEN)
    else:
        raise RuntimeError("No socket to listen on. `LISTEN` config value is empty.")
    if wsgi.warmup.status_code != 200:
        log.error(
            "Warmup failed with status code %s. Shutting down.", wsgi.warmup.status_code
        )
        exit(1)
    wsgi_server.print_listen("Serving on {}:{}")
    systemd_notify("READY=1")
    wsgi_server.run()


# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Middleware for logging requests, using Apache combined log format
class TransLogger(object):
    """
    This logging middleware will log all requests as they go through.
    They are, by default, sent to a logger named ``'wsgi'`` at the
    INFO level.

    If ``setup_console_handler`` is true, then messages for the named
    logger will be sent to the console.
    """

    format = (
        "%(REMOTE_ADDR)s - %(REMOTE_USER)s [%(time)s] "
        '"%(REQUEST_METHOD)s %(REQUEST_URI)s %(HTTP_VERSION)s" '
        '%(status)s %(bytes)s "%(HTTP_REFERER)s" "%(HTTP_USER_AGENT)s"'
    )

    def __init__(
        self,
        application,
        logger=None,
        format=None,
        logging_level=logging.INFO,
        logger_name="wsgi",
        setup_console_handler=True,
        set_logger_level=logging.DEBUG,
    ):
        if format is not None:
            self.format = format
        self.application = application
        self.logging_level = logging_level
        self.logger_name = logger_name
        if logger is None:
            self.logger = logging.getLogger(self.logger_name)
            if setup_console_handler:
                console = logging.StreamHandler()
                console.setLevel(logging.DEBUG)
                # We need to control the exact format:
                console.setFormatter(logging.Formatter("%(message)s"))
                self.logger.addHandler(console)
                self.logger.propagate = False
            if set_logger_level is not None:
                self.logger.setLevel(set_logger_level)
        else:
            self.logger = logger

    def __call__(self, environ, start_response):
        start = time.localtime()
        req_uri = quote(environ.get("SCRIPT_NAME", "") + environ.get("PATH_INFO", ""))
        if environ.get("QUERY_STRING"):
            req_uri += "?" + environ["QUERY_STRING"]
        method = environ["REQUEST_METHOD"]

        def replacement_start_response(status, headers, exc_info=None):
            # @@: Ideally we would count the bytes going by if no
            # content-length header was provided; but that does add
            # some overhead, so at least for now we'll be lazy.
            bytes = None
            for name, value in headers:
                if name.lower() == "content-length":
                    bytes = value
            self.write_log(environ, method, req_uri, start, status, bytes)
            return start_response(status, headers)

        return self.application(environ, replacement_start_response)

    def write_log(self, environ, method, req_uri, start, status, bytes):
        if bytes is None:
            bytes = "-"
        if time.daylight:
            offset = time.altzone / 60 / 60 * -100
        else:
            offset = time.timezone / 60 / 60 * -100
        if offset >= 0:
            offset = "+%0.4d" % (offset)
        elif offset < 0:
            offset = "%0.4d" % (offset)
        remote_addr = "-"
        if environ.get("HTTP_X_FORWARDED_FOR"):
            remote_addr = environ["HTTP_X_FORWARDED_FOR"]
        elif environ.get("REMOTE_ADDR"):
            remote_addr = environ["REMOTE_ADDR"]
        d = {
            "REMOTE_ADDR": remote_addr,
            "REMOTE_USER": environ.get("REMOTE_USER") or "-",
            "REQUEST_METHOD": method,
            "REQUEST_URI": req_uri,
            "HTTP_VERSION": environ.get("SERVER_PROTOCOL"),
            "time": time.strftime("%d/%b/%Y:%H:%M:%S ", start) + offset,
            "status": status.split(None, 1)[0],
            "bytes": bytes,
            "HTTP_REFERER": environ.get("HTTP_REFERER", "-"),
            "HTTP_USER_AGENT": environ.get("HTTP_USER_AGENT", "-"),
        }
        message = self.format % d
        self.logger.log(self.logging_level, message)
