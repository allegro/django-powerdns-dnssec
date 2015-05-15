FROM ubuntu:vivid
MAINTAINER Szymon Pyżalski <szymon.pyzalski@allegro.pl>
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get install -y build-essential python3.4 python3.4-dev curl git libmysqlclient-dev mysql-client netcat
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.4
RUN pip install django==1.7 mysqlclient
RUN pip install git+https://szymon.pyzalski@stash.allegrogroup.com/scm/pylabs/dnsaas.git@develop
ADD example example
ADD startup.sh startup.sh
ADD createdb.sql createdb.sql
CMD bin/bash ./startup.sh
