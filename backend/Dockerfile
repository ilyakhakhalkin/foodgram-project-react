FROM python:3.7-slim

WORKDIR /back

COPY . .
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip3 install psycopg2

RUN pip3 install -r requirements.txt --no-cache-dir

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000