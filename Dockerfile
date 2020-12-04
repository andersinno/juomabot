FROM python:3.6

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -U pip --no-cache && \
    pip install -r requirements.txt uwsgi --no-cache

COPY . /code

ENV ADMIN_PASSWORD hackme
ENV DATABASE_URL sqlite:///juomabot.sqlite3

ENTRYPOINT  ["uwsgi", "--http-socket", ":8000", "--wsgi", "juomabot.wsgi"]
