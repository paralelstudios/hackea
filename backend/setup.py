# -*- coding: utf-8 -*-
"""
    aidex
    ~~~~~~~
    aidex's backend
"""

from setuptools import setup, find_packages


def get_long_description():
    with open('README.md') as f:
        result = f.read()
    return result


setup(
    name='aidex',
    version='0.0.1',
    url='https://github.com/paralelstudios/aidex',
    author='Michael Pérez',
    author_email='mpuhrez@paralelstudios.com',
    description="AIDEX's backend",
    long_description=get_long_description(),
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
)
