#!/bin/bash

. scripts/_select_docker_compose.sh

$DOCKER_COMPOSE -f ./docker-compose.infra.yml --profile=manual_dev --profile=manual_setup down
$DOCKER_COMPOSE -f ./docker-compose.yml down
$DOCKER_COMPOSE -f ./docker-compose.yml up -d
