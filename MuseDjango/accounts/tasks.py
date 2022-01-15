from celery import shared_task
from django.db.models import Count
from .models import *
from config.settings import MUSE_SLACK_TOKEN, DEV
from common.slack_api import slack_post_message
import logging

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
            "!! 🛠 유저 스코어 계산 및 뱃지 지급 완료 !!",
        )
    except:
        logging.error("ERROR: CALC USER SCORE")


# @shared_task
# def calc_ranking():
#     try:
#         queryset = UserProfile.objects.filter(user__is_superuser=False).order_by("-score")

#     except:
#         logging.error("ERROR: CALC RANKING")
