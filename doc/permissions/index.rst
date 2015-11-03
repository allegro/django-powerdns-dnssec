===============================
Notes on permission system
===============================

In order to allow wide range of users to access your company's DNSaaS the
``django-powerdns-dnssec`` offers a permission system to prohibit unwanted
changes. If you do not need any restrictions, simply register all your users
as superusers in django.

The permissions are controlled primarily by the 'owner' field of a Domain or
Record, which is automatically set to the user that created the object. By
default this is the only user that can modify it. Adding records to domains and
subdomaining domains is also restricted.

TODO:

* Authorisations
* Requests
