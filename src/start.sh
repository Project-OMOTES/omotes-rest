#!/bin/bash

set -e

echo "Upgrading SQL schema."
alembic upgrade head
echo "Starting orchestrator."
gunicorn omotes_rest.main:app --config gunicorn.conf.py
