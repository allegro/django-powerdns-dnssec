flake:
	flake8 --exclude migrations dnsaas/ powerdns/

install:
	pip install -e . .[dnsaas]

install-test: install
	pip install .[tests]

test:
	python manage.py test

coveralls:
	coverage run $(shell which python) manage.py test
	coverage report
