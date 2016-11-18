#!/usr/bin/env python

import json
import os
try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages


with open(
    os.path.join(os.path.dirname(__file__), 'README.rst'),
    encoding='utf-8'
) as f:
    long_description = f.read()

with open('version.json') as f:
    version = '.'.join(str(part) for part in json.load(f))

setup(
    name = 'django-powerdns-dnssec',
    version = version,
    url = 'http://bitbucket.org/ambv/django-powerdns/',
    license = 'BSD',
    description = 'PowerDNS administration app for Django',
    long_description = long_description,
    author = 'Peter Nixon, Łukasz Langa, pylabs Team',
    author_email = 'pylabs@allegro.pl',
    packages = [p for p in find_packages() if not p.startswith('example')],
    include_package_data = True,
    platforms = 'any',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = [
        'Django==1.8.13',
        'django-autocomplete-light==2.3.3',
        'django-extensions>=1.5.5',
        'django-nose>=1.4',
        'dj.choices>=0.10.0',
        'mysqlclient==1.3.7',
        'nose-cov>=1.6',
        'factory_boy>=2.5.2',
        # 3.3.3 includes bug, https://github.com/rtfd/readthedocs.org/issues/2101
        'djangorestframework==3.3.2',
        'django-rest-swagger==0.3.8',
        'django-filter==0.15.2',
        'django-threadlocals>=0.8',
        'docutils>=0.12',
        'rules>=0.4',
        'raven==5.20.0'
    ],
    zip_safe = False,  # if only because of the readme file
)
