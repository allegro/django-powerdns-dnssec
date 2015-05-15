FROM ubuntu:vivid
MAINTAINER Szymon Pyżalski <szymon.pyzalski@allegro.pl>
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get install -y build-essential python3.4 python3.4-dev curl git libmysqlclient-dev mysql-client netcat libyaml-dev
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.4
RUN pip install django==1.7 mysqlclient pyyaml
RUN mkdir dnsaas
ADD dnsaas dnsaas/dnsaas
ADD powerdns dnsaas/powerdns
ADD docker dnsaas/docker
ADD setup.py dnsaas/setup.py
ADD manage.py dnsaas/manage.py
ADD MANIFEST.in dnsaas/MANIFEST.in
ADD README.rst dnsaas/README.rst
RUN pip install ./dnsaas
CMD bin/bash dnsaas/docker/startup.sh
