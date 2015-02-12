PowerDNS Example Project
========================

The 'example' directory contains a ready made Django project that should
"just work" in the same way that any standard Django app does.

If you are using Django < 1.7, install South::

  $ pip install south

Then create and migrate the database::

  $ python manage.py syncdb
  $ python manage.py migrate

Finally, run the web server::

  $ python manage.py runserver

The app is available under http://127.0.0.1:8000/.

Using a custom database
-----------------------

By default, the database is created in ``/tmp/powerdns.sqlite``. If you'd
like to use an alternative path or database engine, create
a ``settings_local.py`` file next to ``settings.py`` and provide an alternative
``DATABASES`` dictionary. For example::

  DATABASES = {
      'default': {
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
