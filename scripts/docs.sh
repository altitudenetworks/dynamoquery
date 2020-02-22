#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $(realpath $0)))
cd $ROOT_PATH

echo `git config --get remote.origin.url`
handsdown --external `git config --get remote.origin.url` -n dynamo-query dynamo_query --exclude '*/build/*' --cleanup --panic
