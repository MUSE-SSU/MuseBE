from rest_framework import serializers
from .models import *


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ("title", "content")


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ("title", "content")
