FROM zefciu/python-base
MAINTAINER Pylabs <pylabs@allegro.pl>
RUN pip install nose py3dns requests
ADD test test
ADD runtests.sh runtests.sh
CMD bin/sh runtests.sh
