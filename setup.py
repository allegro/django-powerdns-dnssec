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
    name = "django-powerdns",
    version = "0.2",
    url = 'http://bitbucket.org/peternixon/django-powerdns/',
    download_url = 'http://bitbucket.org/peternixon/django-powerdns/downloads/',
    license = 'BSD',
    description = "PowerDNS administration module for Django",
    author = 'Peter Nixon',
    author_email = 'listuser@peternixon.net',
    packages = find_packages(),
    include_package_data = True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
    install_requires=[
        'Django>=1.2',
    ]
    long_description = """\
Django PowerDNS
===============

Welcome to the PowerDNS module for Django.

This module allows easy administration of PowerDNS records stored in an SQL database by leveraging
the standard Django Admin module. You may also use the Django PowerDNS module as part of a larger
project to programatically modify your DNS records.
"""
)
