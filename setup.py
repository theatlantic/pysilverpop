#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='pysilverpop',
    version='0.2.0',
    author='The Atlantic',
    author_email='programmers@theatlantic.com',
    url='https://github.com/theatlantic/pysilverpop',
    description='Python wrapper for Silverpop.',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=[
        'six',
        'requests',
        'requests_oauthlib',
    ],
    classifiers=[],
    test_suite='silverpop.tests',
)

