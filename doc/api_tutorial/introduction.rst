Introduction
======================

To start the server to test API, consult
:doc:`this instructions<../installation/testing>`


Browsing API documentation
=================================

`swagger_` is used to generate API documentation. Navigate to
http://127.0.0.1:8080/api-docs to browse the documentation.

Sending API requests
============================

Please note, that ``django-powerdns-dnssec`` uses `rest_framework`_ to handle
the API access. Therefore all the perks offered by it are available. Including
the web browsable API. If you navigate to http://127.0.0.1:8080/api you should
see a nice interface where you can play around with the API without any
additional tools.
.. _`rest_framework` http://www.django-rest-framework.org/

Of course you can also send API requests with your favourite library or browser
plugin.
