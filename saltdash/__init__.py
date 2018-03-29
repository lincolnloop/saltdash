import base64
import os
import sys

from goodconf import GoodConf, Value

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saltdash.settings")

config = GoodConf(description="Configuration for saltdash",
                  file_env_var='SALTDASH_CONF',
                  default_files=['saltdash.yml', '/etc/saltdash.yml'])
config.define_values(
    Value('DEBUG', default=False, help="Enable debugging."),
    Value('SECRET_KEY',
          initial=lambda: base64.b64encode(os.urandom(60)).decode(),
          help="a long random string you keep secret "
          "https://docs.djangoproject.com/en/2.0/ref/settings/#secret-key"),
    Value('DATABASE_URL', default='postgres://localhost:5432/salt'),
    Value('ALLOWED_HOSTS', default=['*'], help="Hosts allowed to serve the "
          "site "
          "https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts"),
    Value('GITHUB_TEAM_ID', default=''),
    Value('GITHUB_CLIENT_ID', default=''),
    Value('GITHUB_CLIENT_SECRET', default=''),
    Value('SENTRY_DSN', default='')
)


def manage():
    from goodconf.contrib.django import execute_from_command_line_with_config
    execute_from_command_line_with_config(config, sys.argv)


def generate_config():
    print(config.generate_yaml())
