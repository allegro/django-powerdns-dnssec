#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = 'django-powerdns',
    version = '0.9.0',
    url = 'http://bitbucket.org/peternixon/django-powerdns/',
    download_url = 'http://bitbucket.org/peternixon/django-powerdns/downloads/',
    license = 'BSD',
    description = 'PowerDNS administration module for Django',
    long_description=read('README.rst'),
    author = 'Peter Nixon, Łukasz Langa',
    author_email = 'listuser@peternixon.net',
    packages = [p for p in find_packages() if not p.startswith('example')],
    include_package_data = True,
    platforms='any',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Django>=1.3.4',
        'ipaddr>=2.1.7',
    ],
    zip_safe = False, # if only because of the readme file
)
