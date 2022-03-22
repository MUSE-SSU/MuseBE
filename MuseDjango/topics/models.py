from django.db import models


class Topic(models.Model):
    idx = models.AutoField(primary_key=True)
    topic = models.CharField(max_length=128, verbose_name="주제", default="자유")
    week = models.IntegerField(default=0, verbose_name="주차", null=False, blank=False)
    activate_week = models.BooleanField(default=True, verbose_name="현재 진행 주차")
    created_at = models.DateTimeField(verbose_name="생성 날짜", auto_now_add=True)

    class Meta:
        db_table = "MUSE_Topics"
        verbose_name_plural = "콘테스트 주제"
