#!/bin/sh

python3 manage.py crontab add

exec "$@"