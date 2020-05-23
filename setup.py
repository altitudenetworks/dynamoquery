#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict, List

from setuptools import find_packages, setup

ROOT_PATH = Path(__file__).absolute().parent
README_PATH = ROOT_PATH / "README.md"
DESCRIPTION = README_PATH.read_text().split("\n")[0]
URL = f"https://github.com/altitudenetworks/{ROOT_PATH.name}"

if not README_PATH.exists():
    raise ValueError("README.md file does not exists")

version = (ROOT_PATH / "dynamo_query" / "version.txt").read_text().strip()

#######################################
# USER INPUTS:
REQUIRES_PYTHON = ">=3.6.10"
AUTHOR = "Altitude Networks Engineering Team"
AUTHOR_EMAIL = "engineering@altitudenetworks.com"

# Required Packages
REQUIRED = [
    i.strip() for i in (ROOT_PATH / "requirements.txt").read_text().split("\n") if i.strip()
]

# EXTERNAL DEPENDENCY LINKS
DEPENDENCY_LINKS = []  # type: List[str]

# Optional Packages
EXTRAS = {}  # type: Dict[str, str]

PACKAGE_DATA = {"dynamo_query": ["version.txt"]}


setup(
    name="dynamoquery",
    version=version,
    description=DESCRIPTION,
    long_description=README_PATH.read_text(),
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*", "__pycache__", "examples"]
    ),
    package_data=PACKAGE_DATA,
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    zip_safe=False,
    dependency_links=DEPENDENCY_LINKS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Typing :: Typed",
    ],
)
