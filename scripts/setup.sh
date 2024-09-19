#!/bin/bash
. scripts/_select_docker_compose.sh
. scripts/_load_dot_env.sh .env

# Turn off current system
#$DOCKER_COMPOSE stop

# Deploy postgres omotes_rest schema
$DOCKER_COMPOSE -f ./docker-compose.yml down rest_postgres_db
$DOCKER_COMPOSE -f ./docker-compose.yml up -d --wait rest_postgres_db
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d postgres -c 'CREATE DATABASE omotes_rest;'
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -c "CREATE USER ${POSTGRES_USERNAME} WITH PASSWORD '${POSTGRES_PASSWORD}';"
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -c "ALTER USER ${POSTGRES_USERNAME} WITH PASSWORD '${POSTGRES_PASSWORD}';"
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -c "GRANT ALL PRIVILEGES ON DATABASE omotes_rest TO ${POSTGRES_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${POSTGRES_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${POSTGRES_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRES_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${POSTGRES_USERNAME};"

# Upgrade omotes_rest tables
$DOCKER_COMPOSE -f ./docker-compose.yml build rest_postgres_db_upgrade
$DOCKER_COMPOSE -f ./docker-compose.yml run --rm rest_postgres_db_upgrade
