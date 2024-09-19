#!/bin/bash

if [[ "$OSTYPE" != "win32" && "$OSTYPE" != "msys" ]]; then
  . .venv/bin/activate
fi

pip-compile -U --output-file=requirements.txt pyproject.toml
pip-compile -U --extra=dev -c requirements.txt --output-file=dev-requirements.txt pyproject.toml
