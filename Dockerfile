FROM python:3.4.9-alpine3.7

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -U pip --no-cache && \
    pip install -r requirements.txt gunicorn --no-cache && \
    mkdir /juomabot

COPY . /code

ENV ADMIN_PASSWORD hackme
ENV DATABASE_URL sqlite:///juomabot/juomabot.sqlite3

ENTRYPOINT  ["gunicorn", "juomabot.wsgi"]
