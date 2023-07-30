#!/bin/bash

cd $(dirname $(readlink -e $0))

source .venv/bin/activate

export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1
export PYTHONHASHSEED=1

set -a
source .env

exec python -u main.py
