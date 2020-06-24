#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='pysilverpop',
    version='0.2.6',
    author='The Atlantic',
    author_email='programmers@theatlantic.com',
    url='https://github.com/theatlantic/pysilverpop',
    description='Python wrapper for Acoustic (formerly Silverpop).',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    platforms='any',
    zip_safe=False,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=[
        'six',
        'requests',
        'requests_oauthlib',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='silverpop.tests',
)
