from .models import *
from musepost.models import Post
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField(read_only=True)
    post_title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ("post", "post_title", "category", "count", "is_read", "created_at")

    def get_post_title(self, obj):
        return obj.post.title

    def get_is_read(self, obj):
        return obj.is_read
