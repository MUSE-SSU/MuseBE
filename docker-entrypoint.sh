#!/bin/sh 

echo "-----Django Migration-----"
# python3 manage.py makemigrations --noinput --merge
# python3 manage.py makemigrations --noinput
# python3 manage.py migrate
# python3 manage.py migrate --fake
# python3 manage.py collectstatic --noinput

echo "-----Collect Static-----"
python3 manage.py collectstatic --noinput

echo "-----Start Gunicorn-----"
exec gunicorn config.wsgi:application \
        --name muse \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --timeout 300 &

echo "-----Nginx Start-----"
exec service nginx start

echo "==> Finish!"