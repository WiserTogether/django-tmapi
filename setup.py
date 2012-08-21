#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='django-tmapi',
    version='0.0.1',
    description='A django implementation of Topic Maps API 2.0',
    author='Jamie Norrish',
    author_email='jamie@artefact.org.nz',
    url='http://github.com/wisertoghether/django-tmapi/',
    long_description=open('README.rst', 'r').read(),
    packages=[
        'tmapi',
    ],
    package_data={
    },
    zip_safe=False,
    requires=[
    ],
    install_requires=[
    ],
    classifiers=[
        'Development Status :: Pre Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Apache',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
