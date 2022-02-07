from .models import *
from musepost.models import Post
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField(read_only=True)
    post_title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ("post", "post_title", "category", "count", "is_read", "created_at")
        # 여기서 count는 읽지않은 각 알림 카테고리별 count
        # ex) 해당 게시글(post_idx)에 3개의 좋아요를 받았어요!

    def get_post_title(self, obj):
        return obj.post.title

    def get_is_read(self, obj):
        return obj.is_read
