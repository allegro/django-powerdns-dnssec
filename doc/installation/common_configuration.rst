Common configuration options
===================================

Customizing resource record types
--------------------------------------

If you're not using DNSSEC or the other less common record types, you can
simplify the user interface even more by specifying a sequence of types the app
should use. Simply put this in your ``settings.py``::

  POWERDNS_RECORD_TYPES = (
      'A', 'AAAA', 'CNAME', 'HINFO', 'MX', 'NAPTR', 'NS',
      'PTR', 'SOA', 'SRV', 'TXT',
  )

Consult PowerDNS documentation for a `list of supported resource record types
<http://doc.powerdns.com/types.html>`_.

Notifications
------------------------

This app notifies owners of domains and records that were created for them. To
have them working you need to:

* enable them by setting ``ENABLE_OWNER_NOTIFICATIONS``

* configure ``FROM_EMAIL`` (the e-mail that would be a sender of the
  notifications) 

* configure ``OWNER_NOTIFICATIONS`` as following::

    OWNER_NOTIFICATIONS = {
        'Domain': (subject, content),
        'Record': (subject, content),
    }

* set up the `mailing backend
  <https://docs.djangoproject.com/en/1.8/topics/email/#email-backends>`_


In the subject and content strings you can place the following placeholders:

* ``object`` - the string representation of the domain or record created
* ``owner-email``
* ``owner-name``
* ``creator-email``
* ``creator-name``


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
  $ python manage.py migrate --database==powerdns powerdns

Note that the ``powerdns`` database will maintain its own separate
migration history table. This is especially helpful if your connecting several
Django projects to a single PowerDNS database.

