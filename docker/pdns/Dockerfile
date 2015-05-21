FROM ubuntu:vivid

RUN apt-get update && apt-get install -yq curl build-essential libcurl3 libboost-dev libboost-program-options-dev libboost-serialization-dev libmysqlclient-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN curl -sS https://downloads.powerdns.com/releases/pdns-3.4.4.tar.bz2 | tar xjf - -C . && \
    cd pdns-* && ./configure --with-modules="gmysql" && make && make install && \
    cd .. && rm -fr pdns-*
EXPOSE 53/udp 53/tcp
ADD pdns.conf /usr/local/etc/pdns.conf
CMD /usr/local/sbin/pdns_server --daemon=no --loglevel=9
