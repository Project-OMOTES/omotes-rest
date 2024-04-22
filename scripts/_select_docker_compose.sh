#!/bin/bash

DOCKER_COMPOSE="docker compose"
if ! $(docker compose -v &> /dev/null)
then
    echo "docker compose could not be found. Trying docker-compose"

    DOCKER_COMPOSE="docker-compose"
    if ! $(docker-compose -v &> /dev/null)
    then
      echo "Neither docker-compose nor docker compose could be found. Please install it.."
      exit
    fi
fi

echo "Using '${DOCKER_COMPOSE}' for docker compose command."
