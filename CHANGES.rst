Change Log
----------

2.0
~~~~~

* Templates for domains and records
* Automated PTR
* Domain and record ownership
* REST API via django_rest_framework
* Lot of validation improvements
* Improved unittest code coverage
* Added integration tests via docker
* Created docker configuration for testing purposes

0.9.3
~~~~~

* Fixed issue #3: HTTP 500 in record admin form if no type given

0.9.2
~~~~~

* Fixed issue #2: numeric sorting of IP addresses in admin

0.9.1
~~~~~

* Domain foreign keys support auto completion and have "Edit separately" links
  
* Field choices use radio selects whenever that makes sense (fever clicks
  necessary)

* Forward/reverse domain filter (requires Django 1.4+)

* The ``0002`` database migration in 0.9.0 was incomplete, this is now fixed

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
