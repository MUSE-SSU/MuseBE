'''
from __future__ import absolute_import

import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


schedule = {
    "select-muse": {
        "task": "musepost.tasks.select_muse",
        "schedule": crontab(minute=0, hours=15, day_of_week="sat"),
    },
    "test": {
        "task": "musepost.tasks.test",
        "schedule": crontab(minute=1),
    }
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
'''