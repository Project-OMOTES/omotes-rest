#!/bin/bash
. scripts/_select_docker_compose.sh
. scripts/_load_dot_env.sh .env

# Turn off current system
#$DOCKER_COMPOSE stop

# Deploy postgres omotes_rest schema
$DOCKER_COMPOSE -f ./docker-compose.yml down rest_postgres_db
$DOCKER_COMPOSE -f ./docker-compose.yml up -d --wait rest_postgres_db

$DOCKER_COMPOSE -f ./docker-compose.yml exec rest_postgres_db psql -d omotes_rest -v PG_USERNAME=$POSTGRES_USERNAME -v PG_PASSWORD=$POSTGRES_PASSWORD -v PG_DB=omotes_rest -f /setup/init.sql
