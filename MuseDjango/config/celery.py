from __future__ import absolute_import
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

# Celery 모듈을 위한 Django 기본세팅
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# 여기서 문자열을 사용하는것은 작업자가가 자식 프로세스 직렬화 구성을 하지 않는것을 의미합니다.
# -namespace='CELERY' 의 의미는 셀러리와 관련된 모든 설정은 CELERY_ 라는 prefix로 시작함을 의미
app.config_from_object("django.conf:settings", namespace="CELERY")

# Django 에 등록된 모든 task 모듈을 로드합니다.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # 매주 일요일 자정 - 뮤즈 선정/이번 주 색상 선정/게시물 상태 변경
    "select_weekly_tasks": {
        "task": "musepost.tasks.select_weekly_tasks",
        "schedule": crontab(minute=0, hour=0, day_of_week="sunday"),
    },
    # 매일 새벽 4시 마다- 게시물 색상 추출
    "extract_image_color": {
        "task": "musepost.tasks.get_image_color",
        "schedule": crontab(minute=0, hour=4),
    },
    # # 매일 자정 - 사용하는 게시물이 없는 해시태그 삭제
    # "delete_hashtag_not_use": {
    #     "task": "musepost.tasks.remove_all_tags_without_objects",
    #     "schedule": crontab(minute=0, hour=0),
    # },
    # 매일 1시간 마다 - 유저 Score 계산 후 뱃지 지급
    "calc_user_score": {
        "task": "accounts.tasks.calc_user_score_to_badge",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    # 매주 일요일 자정 - 새로 가입한 유저 리스트 슬랙 전달
    "slack_to_new_user_list": {
        "task": "accounts.tasks.get_new_user_list",
        "schedule": crontab(minute=0, hour=0, day_of_week="sunday"),
    },
}


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
