#!/usr/bin/env python
from setuptools import find_packages, setup
from setuptools.command.develop import develop

class InitDevelop(develop):

    def run(self):
        develop.run(self)
        self._generate_env()

    def _generate_env(self):
        import os
        import string
        import base64
        if os.path.exists('.env'):
            return
        with open('.env.template') as template, open('.env', 'w') as output:
            t = string.Template(template.read())
            output.write(t.safe_substitute({
                'secret_key': base64.b64encode(os.urandom(60)).decode()
            }))


setup(
    name='saltdash',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'saltdash = saltdash:manage',
            'manage.py = saltdash:manage',
        ]
    },
    extra_require={'production': 'uWSGI==2.0.15'},
    cmdclass={'develop': InitDevelop},
)
