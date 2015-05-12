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
    return open(
        os.path.join(os.path.dirname(__file__), fname),
        encoding='utf-8',
    ).read()

setup(
    name = 'django-powerdns-dnssec',
    version = '0.10.0',
    url = 'http://bitbucket.org/ambv/django-powerdns/',
    license = 'BSD',
    description = 'PowerDNS administration app for Django',
    long_description = read('README.rst'),
    author = 'Peter Nixon, Łukasz Langa',
    author_email = 'lukasz@langa.pl',
    packages = [p for p in find_packages() if not p.startswith('example')],
    include_package_data = True,
    platforms = 'any',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = [
        'Django>=1.4',
        'IPy==0.82a',
        'django-extensions==1.5.0',
        'django-nose==1.4',
        'nose-cov==1.6',
    ],
    zip_safe = False,  # if only because of the readme file
)
