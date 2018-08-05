#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open('README.rst', 'rb') as readme_file:
    readme = readme_file.read().decode('utf-8')

requirements = []

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Günther Jena",
    author_email='guenther@jena.at',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Carefully crafted library to operate with continuous " +
                "streams of data in a reactive style with publish/subscribe " +
                "and broker functionality.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='broker publisher subscriber reactive',
    name='broqer',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/semiversus/python-broqer',
    version='0.4.2-dev',
    zip_safe=False,
)
