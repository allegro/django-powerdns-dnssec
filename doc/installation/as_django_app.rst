Installation as django application
====================================

Use pip to install ``django-powerdns-dnssec`` and all its dependencies from PyPI:

.. code-block:: bash

    $ pip install django-powerdns-dnssec

then add ``powerdns`` and ``django_extensions`` to ``INSTALLED_APPS`` in your project's ``settings.py``:

..code-block:: python

    INSTALLED_APPS = [
        # ...
        'powerdns',
        # ...
    ]
