#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $(realpath $0)))

rm -rf build *.egg-info dist/*
python setup.py build bdist_wheel
twine upload --non-interactive dist/*
rm -rf build *.egg-info dist/*
