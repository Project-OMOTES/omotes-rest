#!/bin/bash

docker compose -f ../docker-compose.dev.yml down rest_postgres_db
docker compose -f ../docker-compose.dev.yml up --wait rest_postgres_db_dev
