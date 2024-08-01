#!/bin/bash

. scripts/_select_docker_compose.sh

$DOCKER_COMPOSE -f ./docker-compose.dev.yml -f ./docker-compose.override.dev.yml --profile=manual_dev --profile=manual_setup down
$DOCKER_COMPOSE -f ./docker-compose.yml -f ./docker-compose.override.dev.yml down
$DOCKER_COMPOSE -f ./docker-compose.yml -f ./docker-compose.override.dev.yml up --wait --build
