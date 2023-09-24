#!/usr/bin/env bash

set -e
set -x

pytest --cov=pycosmiconfig --cov-report=term-missing pycosmiconfig/tests "${@}"
