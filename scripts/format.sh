#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place pycosmiconfig --exclude=__init__.py
black pycosmiconfig
isort pycosmiconfig
