#!/bin/bash

cd $(dirname $(readlink -e $0))

export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1
export PYTHONHASHSEED=1

python="$(poetry env info --path)/bin/python"

exec $python -u main.py
