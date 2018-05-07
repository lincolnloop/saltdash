import base64
import os

from goodconf import GoodConf, Value

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saltdash.settings")


class Config(GoodConf):
    """Configuration for saltdash"""
    DEBUG = Value(default=False, help="Enable debugging.")
    SECRET_KEY = Value(
        initial=lambda: base64.b64encode(os.urandom(60)).decode(),
        help="a long random string you keep secret "
        "https://docs.djangoproject.com/en/2.0/ref/settings/#secret-key")
    DATABASE_URL = Value(default='postgres://localhost:5432/salt')
    ALLOWED_HOSTS = Value(default=['*'], help="Hosts allowed to serve the "
        "site "
        "https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts")
    GITHUB_TEAM_ID = Value(default='')
    GITHUB_CLIENT_ID = Value(default='')
    GITHUB_CLIENT_SECRET = Value(default='')
    SENTRY_DSN = Value(default='')


config = Config(file_env_var='SALTDASH_CONF',
                default_files=['saltdash.yml', '/etc/saltdash.yml'])
