"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE, distributed with this software.

Created on June, 2018
"""
from setuptools import setup, find_packages

setup(
    name='magicattr',
    version='0.1.5',
    author='frmdstryr',
    author_email='frmdstryr@gmail.com',
    url='https://github.com/frmdstryr/magicattr',
    description='A getattr and setattr that works on nested objects, lists, '
                'dicts, and any combination thereof without resorting to eval',
    license="MIT",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    py_modules=['magicattr'],
)
