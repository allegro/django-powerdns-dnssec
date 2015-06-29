Auto PTR
================

Normally when you create an A record, you also want to create a PTR record.
This can be automated by setting the auto_ptr option when creating the A
record. If there is no domain for the PTR record, a new one will be created:

* If the domain where you created the A record has ``reverse_template``
  specified, this template will be used to created the domain for PTR.
* Otherwise the template with name specified in
  DNSAAS_DEFAULT_REVERSE_DOMAIN_TEMPLATE setting will be used.
