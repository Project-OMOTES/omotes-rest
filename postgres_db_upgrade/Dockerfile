FROM python:3.11-slim-buster

RUN mkdir -p /app/postgres_db_upgrade/
WORKDIR /app/rest_postgres_db_upgrade/

# for psycopg2
RUN apt-get update
RUN apt-get -y install libpq-dev gcc

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

CMD ["alembic", "upgrade", "head"]
