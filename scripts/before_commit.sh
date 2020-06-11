#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $(realpath $0)))
cd $ROOT_PATH

# vulture dynamo_query --make-whitelist > vulture_whitelist.py
black **/*.py
isort **/*.py
pylint dynamo_query
mypy dynamo_query
vulture dynamo_query vulture_whitelist.py
pytest -m "not integration"
# pytest --cov-report html --cov dynamo_query

# ./scripts/docs.sh
