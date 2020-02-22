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

if [[ "$VERSION" == "" ]]; then
    echo "No VERSION specified"
    exit 1
fi

if [[ "$GITHUB_EMAIL" == "" ]]; then
    echo "No GITHUB_EMAIL specified"
    exit 1
fi

echo "Bumping version to ${VERSION}"
echo "__version__ = \"${VERSION}\"" > __version__.py

git config --global user.email "${GITHUB_EMAIL}"
git config --global user.name "${GITHUB_ACTOR}"
git pull
if [[ `git diff --stat | grep version` != "" ]]; then
    echo "There are changes: `git diff`"
    git add __version__.py
    git commit -m "Bump version to ${VERSION}"
    git tag ${VERSION}
    git push https://${GITHUB_ACTOR}:${GITHUB_TOKEN}@github.com/altitudenetworks/dynamo_query.git --tags
    git push https://${GITHUB_ACTOR}:${GITHUB_TOKEN}@github.com/altitudenetworks/dynamo_query.git HEAD:master
else
    echo "Version is already up to date."
fi
