## Hackea

A sms-integrated non-profit repository.

## Backend

To get a backend service running, make you have docker (docker-machine, docker-compose) installed.

first create/start your docker machine
```
$ docker-machine create -d virtualbox hackea
$ eval $(docker-machine env hackea)
```

then build up your containers, instatiate them, and run the database migrations
```
$ docker-compose build
$ docker-compose up -d
$ docker-compose run backend alembic upgrade head
```
