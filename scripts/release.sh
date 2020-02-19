#!/usr/bin/env bash
set -e

ROOT_PATH=$(dirname $(dirname $(realpath $0)))

rm -rf build *.egg-info dist/* > /dev/null
python setup.py build bdist_wheel 1>/dev/null 2>/dev/null
twine upload --non-interactive dist/* > /dev/null || true
rm -rf build *.egg-info dist/* > /dev/null
