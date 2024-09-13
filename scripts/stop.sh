#!/bin/bash
. scripts/_select_docker_compose.sh

$DOCKER_COMPOSE -f ./docker-compose.yml --profile=manual_setup down
