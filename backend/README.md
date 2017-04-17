# AIDEX Backend

## Installation

Tools:
* postgres
* python3


Make sure to have Postgres installed and running, if not (mac users) can download [Postgres.app](https://postgresapp.com).

```
$ pip install -r requirements.txt
$ pip install -e .
$ alembic upgrade head
```

To use the shell:

```
$ python manage.py shell
```

To run the server

```
$ python manage.py runserver
```
