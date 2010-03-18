#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages
    
import os

setup(
    name = "django-dyndns",
    version = "0.1",
    url = 'http://bitbucket.org/peternixon/django-dyndns/wiki/Home',
	download_url = 'http://bitbucket.org/peternixon/django-dyndns/downloads/',
    license = 'BSD',
    description = "A small Dynamic DNS Server",
    author = 'Peter Nixon',
    author_email = 'listuser@peternixon.net',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
