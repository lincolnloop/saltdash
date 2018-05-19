"""
If you really really want to run uWSGI instead of the built-in server and you still
wanted to bundle the app with shiv, this is what you're looking for. Run::

    make uwsgi

This will build a library we can load with ctypes and execute as a management command.
"""
import ctypes

from django.core.management import BaseCommand
from django.conf import settings


def run(uwsgi_binary, uwsgi_args):
    # load the uwsgi library in the global namespace
    libpath = str(settings.BASE_DIR / "libuwsgi.so")
    uwsgi = ctypes.CDLL(libpath, mode=ctypes.RTLD_GLOBAL)

    args = [
        uwsgi_binary,
        "--binary-path",
        uwsgi_binary,
        "--module",
        "saltdash.wsgi:application",
        "--static-map",
        "/static={}".format(settings.STATIC_ROOT),
    ] + uwsgi_args

    # build command line args
    argv = (ctypes.c_char_p * (len(args) + 1))()
    for pos, arg in enumerate(args):
        argv[pos] = bytes(arg, "utf-8")
    # inform the uwsgi engine, the passed environ is not safe to overwrite
    envs = (ctypes.c_char_p * 1)()
    # enter into uWSGI !!!
    uwsgi.uwsgi_init(len(args), argv, envs)


class Command(BaseCommand):
    help = "Start uWSGI server"

    # This bypasses any Django handling of the command and sends all arguments straight
    # to uWSGI. App configuration must be done with the default configuration files,
    # environment variables, or the `SALTDASH_CONF` environment variable to point to
    # a custom configuration file.
    def run_from_argv(self, argv):
        run(argv[1], argv[2:])
