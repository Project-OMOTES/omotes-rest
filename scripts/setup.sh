#!/bin/bash
. scripts/_select_docker_compose.sh
. scripts/_load_dot_env.sh .env

# Turn off current system
#$DOCKER_COMPOSE stop

# Deploy postgres omotes schema
$DOCKER_COMPOSE -f ./docker-compose.infra.yml --profile=manual_dev down rest_postgres_db_dev
$DOCKER_COMPOSE -f ./docker-compose.infra.yml up -d --wait rest_postgres_db
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d postgres -c 'CREATE DATABASE omotes;'
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d omotes -c "CREATE USER ${POSTGRESQL_USERNAME} WITH PASSWORD '${POSTGRESQL_PASSWORD}';"
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d omotes -c "ALTER USER ${POSTGRESQL_USERNAME} WITH PASSWORD '${POSTGRESQL_PASSWORD}';"
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d omotes -c "GRANT ALL PRIVILEGES ON DATABASE omotes TO ${POSTGRESQL_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d omotes -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${POSTGRESQL_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d omotes -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRESQL_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d omotes -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${POSTGRESQL_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d omotes -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRESQL_USERNAME};"
$DOCKER_COMPOSE -f ./docker-compose.infra.yml exec rest_postgres_db psql -d omotes -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${POSTGRESQL_USERNAME};"

# Upgrade omotes tables
$DOCKER_COMPOSE -f ./docker-compose.infra.yml build rest_postgres_db_upgrade
$DOCKER_COMPOSE -f ./docker-compose.infra.yml run --rm rest_postgres_db_upgrade
