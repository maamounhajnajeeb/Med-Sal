#!/bin/sh

set -e

python manage.py migrate

uwsgi --socket :8000 --master --enable-threads --module core.wsgi
