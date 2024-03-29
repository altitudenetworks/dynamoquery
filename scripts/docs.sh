#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $(realpath $0)))
cd $ROOT_PATH

handsdown --external `git config --get remote.origin.url` -n dynamo-query dynamo_query --branch master --exclude '*/build/*' --cleanup --panic $@
