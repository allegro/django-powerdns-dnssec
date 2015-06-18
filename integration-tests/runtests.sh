until nc -z -w 4 dnsaas 8080
do
    echo "Waiting for application startup"
    sleep 3
done

nosetests
