from celery import shared_task
from django.db.models import Count
from .models import *
from config.settings import MUSE_SLACK_TOKEN, DEV
from common.slack_api import slack_post_message
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("api")

FIRST_BADGE = 250
SECOND_BADGE = 1000
THIRD_BADGE = 5000
FOURTH_BADGE = 10000
FIFTGH_BADGE = 100000


@shared_task
def calc_user_score_to_badge():
    try:
        logger.info("CALC USER SCORE TO BADGE")
        queryset = UserProfile.objects.all()
        for query in queryset:
            if FIRST_BADGE <= query.score < SECOND_BADGE:
                query.badge = 1
            elif SECOND_BADGE <= query.score < THIRD_BADGE:
                query.badge = 2
            elif THIRD_BADGE <= query.score < FOURTH_BADGE:
                query.badge = 3
            elif FOURTH_BADGE <= query.score < FIFTGH_BADGE:
                query.badge = 4
            elif FIFTGH_BADGE <= query.score:
                query.badge = 5
            else:  # 아무것도 획득 못함
                continue
            query.save()
        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev" if DEV else "#muse-prod",
            "🛠 유저 스코어 계산 및 뱃지 지급 완료",
        )
    except:
        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev-error" if DEV else "#muse-prod-error",
            "ERROR: 유저 스코어 계산 및 뱃지 지급 완료",
        )
        logging.error("ERROR: CALC USER SCORE")


@shared_task
def get_new_user_list():
    try:
        now = datetime.now()
        before_one_week = now - timedelta(weeks=1)
        new_user_list = []
        queryset = User.objects.filter(
            date_joined__lte=now, date_joined__gte=before_one_week
        )
        for q in queryset:
            new_user_list.append((q.nickname, q.profile.insta_id))
        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev" if DEV else "#muse-prod",
            f"🎉 새로운 유저 리스트!! {new_user_list}",
        )
    except:
        logging.error("ERROR: USER LIST TO CSV")
