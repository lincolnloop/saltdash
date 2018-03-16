#!/usr/bin/env python
from setuptools import setup
from setuptools.command.develop import develop

class InitDevelop(develop):

    def run(self):
        develop.run(self)
        self._generate_config()

    def _generate_config(self):
        import os
        import string
        import base64
        if os.path.exists('config.yml'):
            return
        with open('config.yml.template') as template, open('config.yml', 'w') as output:
            t = string.Template(template.read())
            output.write(t.safe_substitute({
                'secret_key': base64.b64encode(os.urandom(60)).decode()
            }))


setup(cmdclass={'develop': InitDevelop})
