from django.contrib import admin
from .models import *


class PostAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "writer",
        "title",
        "image",
        "content",
        "views",
        "likes",
        "topic",
        "week",
        "hashtag",
        "is_contest",
        "cur_status",
        "is_muse",
        "created_at",
        "modified_at",
    ]


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ["idx", "get_post_id", "get_like_user_id"]

    def get_post_id(self, obj):
        return obj.post.idx

    def get_like_user_id(self, obj):
        return obj.like_user.nickname

    get_post_id.short_description = "게시글"  # Renames column head
    get_like_user_id.short_description = "좋아요 누른 유저"  # Renames column head


class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "get_post_id",
        "comment",
        "get_writer_id",
        "created_at",
        "modified_at",
    ]

    def get_post_id(self, obj):
        return obj.post.idx

    def get_writer_id(self, obj):
        return obj.writer.nickname

    get_post_id.short_description = "게시글"  # Renames column head
    get_writer_id.short_description = "댓글 작성자"  # Renames column head


admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(Comment, CommentAdmin)
