#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = 'django-powerdns',
    version = '0.2',
    url = 'http://bitbucket.org/peternixon/django-powerdns/',
    download_url = 'http://bitbucket.org/peternixon/django-powerdns/downloads/',
    license = 'BSD',
    description = 'PowerDNS administration module for Django',
    long_description=read('README.rst'),
    author = 'Peter Nixon',
    author_email = 'listuser@peternixon.net',
    packages = find_packages(),
    include_package_data = True,
    platforms='any',
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
    ],
    install_requires=[
        'Django>=1.2',
    ],
)
