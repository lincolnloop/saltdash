#!/usr/bin/env python
from setuptools import find_packages, setup

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
)
