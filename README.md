## MMAP

A sms-integrated non-profit repository.
1. Michael Pérez
2. Alfredo Llop
3. Marina Osorio
4. Pablo Rivera

## Project Description
Directorio móvil de las agencias sin fines de lucro.
Provee una forma accesible para encontrar la organización que te puede ayudar a través de SMS y un directorio digital móvil.
Crear una interacción entre una persona y las causas que le interesan.
Ayudar a las OSFL a promover su causa y conseguir lo que necesitan, cuando lo necesitan
Ayudar a las comunidades especiales a organizarse, visibilizar sus necesidades y conseguir apoyo

## Backend

To get a backend service running, make you have docker (docker-machine, docker-compose) installed.

first create/start your docker machine
```
$ docker-machine create -d virtualbox aidex
$ eval $(docker-machine env aidex)
```

then build up your containers, instatiate them, and run the database migrations
```
$ docker-compose build
$ docker-compose up -d
$ docker-compose run backend alembic upgrade head
```

finally get the machines ip to make calls to it
```
$ docker-machine ip aidex
```
