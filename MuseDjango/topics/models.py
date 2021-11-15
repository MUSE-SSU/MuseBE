from django.db import models


class Topic(models.Model):
    idx = models.AutoField(primary_key=True)
    topic = models.CharField(max_length=128, verbose_name="주제", null=False, blank=False)
    week = models.IntegerField(default=0, verbose_name="해당 주차", null=False, blank=False)
    activate_week = models.BooleanField(default=False, verbose_name="현재 진행 주차")

    class Meta:
        db_table = "Topics"
