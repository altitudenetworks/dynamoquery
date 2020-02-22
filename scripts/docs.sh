#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $(realpath $0)))
cd $ROOT_PATH

GIT_URL="git@github.com:altitudenetworks/dynamoquery.git"
handsdown --external "$GIT_URL" -n dynamo-query dynamo_query --exclude '*/build/*' --cleanup --panic
