Testing installation
=========================

If you want to just play around with a simple django-powerdns application
without a need to configure mysql and powerDNS on your machine and without a
risk of polluting your DNS, the included docker-compose configuration is best
for you. All you need to do is::

    $ git clone git@github.com:allegro/django-powerdns-dnssec.git
    $ cd django-powerdns-dnssec.git
    $ pip install docker-compose
    $ docker-compose up

This will start for you:

* A working django application exposed on port 8080
* A mysql database (not accessible from outside)
* A PowerDNS server exposed on port 5353

To access the django admin panel, navigate to ``http://127.0.0.1:8080/admin/``.

To query the DNS server you can use e.g. the ``dig`` tool like this::
    
    $ dig @127.0.0.1 -p 5353 www.example.com

    ; <<>> DiG 9.9.5-3ubuntu0.2-Ubuntu <<>> @127.0.0.1 -p 5353 www.example.com
    ; (1 server found)
    ;; global options: +cmd
    ;; Got answer:
    ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 31746
    ;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
    ;; WARNING: recursion requested but not available
    
    ;; OPT PSEUDOSECTION:
    ; EDNS: version: 0, flags:; udp: 1680
    ;; QUESTION SECTION:
    ;www.example.com.               IN      A
    
    ;; ANSWER SECTION:
    www.example.com.        3600    IN      A       192.168.1.11
    
    ;; Query time: 156 msec
    ;; SERVER: 127.0.0.1#5353(127.0.0.1)
    ;; WHEN: Thu Jun 18 09:28:21 CEST 2015
    ;; MSG SIZE  rcvd: 60

The above installation would give you everything you need to go through the
tutorials of this documentation. You should note however that it is not fit for
any production environment. Caching is disabled in this configuration in order
to run integration tests fast.
