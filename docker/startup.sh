#!/bin/sh
# Wait for DB to start up
until nc -z -w 4 db 3306
do
    echo "Can't connect to mysql"
    sleep 3
done
echo "CREATE DATABASE powerdns" | mysql -u root --password=root -h db
python3.4 example/manage.py syncdb --noinput
echo "from django.contrib.auth.models import User; User.objects.create_superuser('dnsaas', 'dnsaas@example.com', 'dnsaas')" | python3.4 example/manage.py shell
python3.4 example/manage.py runserver 0.0.0.0:8000
