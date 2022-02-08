from django.db import models
from accounts.models import User
from musepost.models import Post


NOTI_CATEGORY = (
    ("like", "좋아요"),
    ("bookmark", "북마크"),
    ("comment", "댓글"),
)


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        to_field="user_id",
        on_delete=models.CASCADE,
        related_name="noti",
        verbose_name="알림 유저",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        db_column="post_idx",
        related_name="noti",
        verbose_name="알림 게시글",
    )
    category = models.CharField(
        max_length=50,
        choices=NOTI_CATEGORY,
        verbose_name="알림 카테고리",
    )
    count = models.PositiveIntegerField(default=1, verbose_name="알림 개수")
    is_read = models.BooleanField(default=False, verbose_name="알림 확인 여부")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "MUSE_Notification"
        verbose_name_plural = "알림"
