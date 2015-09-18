Auto PTR
================

Normally when you create an A record, you also want to create a PTR record.

There are three options for auto_ptr on a record:

* **ALWAYS** - create a PTR for every A record
* **NEVER** - don't create PTR's automatically
* **ONLY-IF-DOMAIN-EXISTS** - create PTR if the reverse domain
  is already present

If there is no domain for the PTR record and you selected **ALWAYS**,
a new one will be created:

* If the domain where you created the A record has ``reverse_template``
  specified, this template will be used to created the domain for PTR.
* Otherwise the template with name specified in
  DNSAAS_DEFAULT_REVERSE_DOMAIN_TEMPLATE setting will be used.
