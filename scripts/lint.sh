#!/usr/bin/env bash

set -x

mypy pycosmiconfig
black pycosmiconfig --check
isort --check-only pycosmiconfig
flake8
