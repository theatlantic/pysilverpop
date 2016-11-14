#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='pysilverpop',
    version="0.1.0",
    author='The Atlantic',
    author_email='programmers@theatlantic.com',
    url='https://github.com/theatlantic/pysilverpop',
    description='Python wrapper for Silverpop.',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "requests",
        "requests_oauthlib",
    ],
    classifiers=[
    ],
    test_suite="silverpop.tests",
)

