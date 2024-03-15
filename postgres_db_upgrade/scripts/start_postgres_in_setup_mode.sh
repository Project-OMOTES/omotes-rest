#!/bin/bash

docker compose -f ../docker-compose.infra.yml down rest_postgres_db
docker compose -f ../docker-compose.infra.yml up --wait rest_postgres_db_dev
