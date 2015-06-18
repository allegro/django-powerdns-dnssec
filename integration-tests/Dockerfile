FROM ubuntu:vivid
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get install -y python3.4 curl netcat dnsutils
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.4
RUN pip install nose py3dns requests
ADD test test
ADD runtests.sh runtests.sh
CMD bin/sh runtests.sh
