Common configuration options
===================================

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

If you are using ``django-powerdns-dnssec`` as a part of a larger django
project and this project uses a different database than the one used by
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
