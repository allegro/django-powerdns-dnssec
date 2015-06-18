Domain templates
========================

If you have several "boilerplate" DNS records that you need to configure for
every new domain (most typically this would be SOA and NS records) you can use
domain templates to reduce the amount of work needed.

1. Create a domain template object via admin selecting a name that would fit
   the type of domain that would need the configuration.
2. Create record templates bound to the above domain template. You can create
   record templates in a similar way to records. Anywhere in ``name`` and
   ``content`` fields you can use a placeholder ``{domain-name}`` to insert the
   name of an actual domain.
3. When creating a domain - select the appropriate template. The predefined
   records will be created automatically.

As an example of a domain configuration see the ``reverse`` domain that is
available in ``docker-compose`` installation.
