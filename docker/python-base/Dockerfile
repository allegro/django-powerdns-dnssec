FROM debian:jessie
MAINTAINER Pylabs <pylabs@allegro.pl>
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update && apt-get install -y build-essential python3.4 python3.4-dev curl libmysqlclient-dev mysql-client netcat libyaml-dev && apt-get clean
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.4
