from celery import shared_task
from accounts.models import User
from musepost.models import Post
from .models import *
from config.settings import MUSE_SLACK_TOKEN, DEV
from common.slack_api import slack_post_message

import logging

logger = logging.getLogger("api")


@shared_task
def check_notification(post_idx, noti_category):
    try:
        post = Post.objects.get(idx=post_idx)
        user = User.objects.get(user_id=post.writer)
        # 읽지 않은 알림 중
        noti, is_noti = Notification.objects.get_or_create(
            user=user, post=post, category=noti_category, is_read=False
        )

        if not is_noti:  # 존재함 -> count+1
            noti.count += 1
            noti.save()
        else:  # 존재안함 -> 새로 생성
            pass

        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev" if DEV else "#muse-prod",
            f"🟡 새로운 알림 생성! {user.nickname}::{noti_category}",
        )
    except:
        logger.error("ERROR: CHECK NOTIFICATION")
