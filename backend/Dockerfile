FROM tiangolo/uwsgi-nginx-flask:flask
MAINTAINER Michael Perez "mpuhrez@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install -e .
