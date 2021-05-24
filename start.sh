#!/bin/bash

cd $(dirname $(readlink -e $0))

export PYTHON_UNBUFFERED=1
export PYTHONFAULTHANDLER=1
export PYTHONHASHSEED=1

python="$(poetry env info --path)/bin/python"

exec $python -u main.py
