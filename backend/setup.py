# -*- coding: utf-8 -*-
"""
    hackea
    ~~~~~~~
    hackea's backend
"""

from setuptools import setup, find_packages


def get_long_description():
    with open('README.md') as f:
        result = f.read()
    return result

setup(
    name='hackea',
    version='0.0.1',
    url='https://github.com/paralelstudios/hackea',
    author='Michael Perez',
    author_email='mpuhrez@gmail.com',
    description="Hackea's backend",
    long_description=get_long_description(),
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
)
