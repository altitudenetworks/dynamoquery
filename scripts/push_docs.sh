#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $(realpath $0)))
cd ${ROOT_PATH}

if [[ "$GITHUB_ACTOR" == "" ]]; then
    echo "No GITHUB_ACTOR specified"
    exit 1
fi

if [[ "$GITHUB_TOKEN" == "" ]]; then
    echo "No GITHUB_TOKEN specified"
    exit 1
fi

if [[ "$GITHUB_EMAIL" == "" ]]; then
    echo "No GITHUB_EMAIL specified"
    exit 1
fi

git config --global user.email "${GITHUB_EMAIL}"
git config --global user.name "${GITHUB_ACTOR}"

if [[ `git diff --stat | grep docs` != "" ]]; then
    echo "There are changes: `git diff`"
    git add docs
    git commit -m "Update docs"
    git push https://${GITHUB_ACTOR}:${GITHUB_TOKEN}@github.com/altitudenetworks/dynamoquery.git HEAD:master
else
    echo "Docs are already up to date."
fi
