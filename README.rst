Django PowerDNS
===============

Welcome to the PowerDNS app for Django.

This application allows easy administration of PowerDNS records stored in an
SQL database by leveraging the standard Django Admin app. You may also use the
Django PowerDNS application as part of a larger project to programatically
modify your DNS records.

Quickstart
----------

Simply add ``powerdns`` to ``INSTALLED_APPS`` in your ``settings.py``. Use
South for database migrations.

Using a separate database for PowerDNS
--------------------------------------

If your Django application is using a different database than the one used by
PowerDNS, provide the configuration for the DNS database in ``settings.py`` as
a separate entry in ``DATABASES``, for example::

  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'project_db',
          'USER': 'user',
          'PASSWORD': 'secret',
          'HOST': '127.0.0.1',
          'PORT': '3306',
          'OPTIONS': {
              "init_command": "SET storage_engine=INNODB",
          },
      },
      'powerdns': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'powerdns',
          'USER': 'pdns',
          'PASSWORD': 'pdns',
          'HOST': '127.0.0.1',
          'PORT': '3306',
          'OPTIONS': {
              "init_command": "SET storage_engine=INNODB",
          },
      },
  }

For Django to automatically route ``powerdns`` requests to the right database,
add this setting to ``settings.py``::

  DATABASE_ROUTERS = ['powerdns.routers.PowerDNSRouter']

Authors
-------

Application written by `Peter Nixon <mailto:listuser@peternixon.net>`_ and
`Łukasz Langa <mailto:lukasz@langa.pl>`_.
