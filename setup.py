#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List, Dict

from setuptools import setup
from setuptools import find_packages


ROOT_PATH = Path(__file__).absolute().parent
README_PATH = ROOT_PATH / "README.md"
DESCRIPTION = README_PATH.read_text().split("\n")[0]
URL = f"https://github.com/altitudenetworks/{ROOT_PATH.name}"

if not README_PATH.exists():
    raise ValueError("README.md file does not exists")

try:
    import __version__ as v

    version = v.__version__
except ImportError:
    raise ValueError("__version__.py file does not exists")

#######################################
# USER INPUTS:
REQUIRES_PYTHON = ">=3.6"
AUTHOR = "Altitude Networks Engineering Team"
AUTHOR_EMAIL = "engineering@altitudenetworks.com"

# Required Packages
REQUIRED = [
    "botocore",
    "typing_extensions",
]

# EXTERNAL DEPENDENCY LINKS
DEPENDENCY_LINKS = []  # type: List[str]

# Optional Packages
EXTRAS = {}  # type: Dict[str, str]


setup(
    name="dynamo-query",
    version=version,
    description=DESCRIPTION,
    long_description=README_PATH.read_text(),
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*", "__pycache__"]
    ),
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
