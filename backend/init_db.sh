#! /bin/bash
set -x

if [[ ! -f manage.py ]]; then
    echo "No manage.py, wrong location"
    exit 1
fi

sleep 2
docker rm -f yg-mariadb-dev
docker run -it -d \
    -e MYSQL_ROOT_PASSWORD=ygenter \
    -e MYSQL_DATABASE=ygenter \
    -e MYSQL_USER=ygenter \
    -e MYSQL_PASSWORD=ygenter \
    -p 127.0.0.1:1398:3306 \
    --restart=always \
    --name yg-mariadb-dev \
    mariadb:10.7.1

docker run -it -d \
    -e MONGO_INITDB_ROOT_USERNAME=ygenter \
    -e MONGO_INITDB_DATABASE=ygenter \
    -e MONGO_INITDB_ROOT_PASSWORD=ygenter \
    -p 127.0.0.1:1399:27017 \
    --restart=always \
    --name yg-mongodb-dev \
    mongo:5.0.5

if [ "$1" = "--migrate" ]; then
    sleep 3
    echo `cat /dev/urandom | head -1 | md5sum | head -c 32` > data/config/secret.key
    python manage.py migrate
    python manage.py inituser --username root --password rootroot --action create_super_admin
fi