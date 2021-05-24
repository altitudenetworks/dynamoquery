#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

# vulture dynamo_query --make-whitelist > vulture_whitelist.txt
black **/*.py
isort **/*.py
flake8 dynamo_query
mypy dynamo_query
vulture dynamo_query vulture_whitelist.txt
pytest -m "not integration"
# pytest --cov-report html --cov dynamo_query

# ./scripts/docs.sh
