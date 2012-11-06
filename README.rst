Django PowerDNS with DNSSEC support
===================================

Welcome to the PowerDNS app for Django.

This application allows easy administration of PowerDNS records stored in an
SQL database by leveraging the standard Django Admin app. You may also use the
Django PowerDNS application as part of a larger project to programatically
modify your DNS records.

**Note:** This is an updated and enhanced fork of `django-powerdns
<http://pypi.python.org/pypi/django-powerdns/>`_ which looks abandoned as of
November 2012.

Quickstart
----------

Simply add ``powerdns`` and ``lck.django.common`` to ``INSTALLED_APPS`` in your
``settings.py``.  Use South for database migrations.

Customizing resource record types
---------------------------------

If you're not using DNSSEC or the other less common record types, you can
simplify the user interface even more by specifying a sequence of types the app
should use. Simply put this in your ``settings.py``::

  POWERDNS_RECORD_TYPES = (
      'A', 'AAAA', 'CNAME', 'HINFO', 'MX', 'NAPTR', 'NS',
      'PTR', 'SOA', 'SRV', 'TXT',
  )

Consult PowerDNS documentation for a `list of supported resource record types
<http://doc.powerdns.com/types.html>`_.

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

You have to sync and migrate the ``default`` and the ``powerdns`` databases
separately. First the default database::

  $ python manage.py syncdb
  $ python manage.py migrate

Then the ``powerdns`` database::

  $ python manage.py syncdb --database=powerdns
  $ python manage.py migrate --database==powerdns

Note that the ``powerdns`` database will maintain its own separate South
migration history table. This is especially helpful if your connecting several
Django projects to a single PowerDNS database.

Change Log
----------

0.9.1
~~~~~

* Domain foreign keys support auto completion and have "Edit separately" links
  
* Field choices use radio selects whenever that makes sense (fever clicks
  necessary)

* Forward/reverse domain filter (requires Django 1.4+)

0.9.0
~~~~~

* DNSSEC tables supported.

* Support for multiple databases.

* Updated the project to require at least Django 1.3.

* UI translations supported (currently Polish translation added).

* South migrations.

* Source code compliant with PEP8.

* Minor fixes.

0.2.0
~~~~~

* First release with basic PowerDNS support.

Authors
-------

Application written by `Peter Nixon <mailto:listuser@peternixon.net>`_ and
`Łukasz Langa <mailto:lukasz@langa.pl>`_. NSEC3 code based on George Notaras'
work with `django-powerdns-manager
<https://bitbucket.org/gnotaras/django-powerdns-manager>`_.
