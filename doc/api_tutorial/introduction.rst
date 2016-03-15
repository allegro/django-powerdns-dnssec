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



Filtering
=========

Endpoint `/api/records/`
------------------------

Two extra options are present:

`ip`: gets `records` related to filtering `IP`

    example urls:
        - http://localhost:8080/api/records/?ip=192.168.0.1
            returns all records related to "192.168.0.1" IP
        - http://localhost:8080/api/records/?ip=192.168.0.1&ip=192.168.0.2
            returns all records related to "192.168.0.1" or "192.168.0.2" IPs


`type`: gets `records` related to filtering `types` ('A', 'CNAME', etc.)

    example urls:
        - http://localhost:8080/api/records/?type=NS
            returns all records with type=NS
        - http://localhost:8080/api/records/?type=NS&type=A
            returns all records with type=NS OR type=A
