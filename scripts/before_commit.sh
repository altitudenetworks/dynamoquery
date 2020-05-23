#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $(realpath $0)))
cd $ROOT_PATH

# vulture dynamo_query --make-whitelist > vulture_whitelist.py
vulture dynamo_query vulture_whitelist.py
mypy dynamo_query
pylint dynamo_query
pytest
# pytest --cov-report html --cov dynamo_query

# ./scripts/docs.sh
