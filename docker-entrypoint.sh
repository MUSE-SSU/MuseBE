#!/bin/sh 

if [ "celery" = "$1" ]
then
    celery -A config worker --loglevel=info
elif [ "celerybeat" = "$1" ]
then
    celery -A config beat --loglevel=info # --scheduler django_celery_beat.schedulers:DatabaseScheduler
else
        echo "-----Django Migration-----"
        # python3 manage.py makemigrations --noinput --merge
        # python3 manage.py makemigrations --noinput
        # python3 manage.py migrate
        # python3 manage.py migrate --fake

        echo "-----Collect Static-----"
        # python3 manage.py collectstatic --noinput

        echo "-----Start Gunicorn-----"
        exec gunicorn config.wsgi:application \
                --preload \
                --name muse \
                --bind 0.0.0.0:8000 \
                --workers 4 \
                --timeout 300

        # echo "-----Nginx Start-----"
        # exec service nginx start

fi