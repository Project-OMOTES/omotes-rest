#!/bin/bash

docker compose -f ../docker-compose.dev.yml down rest_postgres_db
docker compose -f ../docker-compose.yml -f ../docker-compose.override.dev.yml up --wait rest_postgres_db
