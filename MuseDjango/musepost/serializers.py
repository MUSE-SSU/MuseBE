from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from .models import *
from accounts.models import *
from config.settings import MEDIA_URL


class PostUploadSerializer(TaggitSerializer, serializers.ModelSerializer):
    hashtag = TagListSerializerField()

    class Meta:
        model = Post
        fields = (
            "title",
            "writer",
            "image",
            "content",
            "week",
            "topic",
            "hashtag",
            "ref_url",
            "is_reference",
            "is_contest",
            "cur_status",
        )


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = "__all__"


class PostDisplayAllSerializer(serializers.ModelSerializer):
    writer = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    writer_avatar = serializers.SerializerMethodField()
    is_login_user_liked = serializers.SerializerMethodField()
    is_writer = serializers.SerializerMethodField()

    class Meta:
        # 무한스크롤 페이지
        model = Post
        fields = (
            "idx",
            "writer",
            "writer_avatar",
            "title",
            "content",
            "image",
            "views",
            "likes",
            "topic",
            "week",
            "is_muse",
            "is_login_user_liked",
            "is_writer",
        )

    # noinspection PyMethodMayBeStatic
    def get_writer_avatar(self, obj):
        if not obj.writer.profile.avatar:
            return MEDIA_URL + "default_avatar.png"
        return MEDIA_URL + str(obj.writer.profile.avatar)

    def get_is_login_user_liked(self, obj):
        try:
            login_user = self.context.get("request").user
        except:
            login_user = None
        return (
            True
            if PostLike.objects.filter(post=obj, like_user=login_user).exists()
            else False
        )

    def get_is_writer(self, obj):
        try:
            login_user = self.context.get("request").user
        except:
            login_user = None
        print(Post.objects.filter(idx=obj.idx, writer=login_user).exists())
        return (
            True
            if Post.objects.filter(idx=obj.idx, writer=login_user).exists()
            else False
        )


class CommentDisplaySerializer(serializers.ModelSerializer):
    writer = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    is_writer = serializers.SerializerMethodField()
    writer_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "idx",
            "writer",
            "writer_avatar",
            "comment",
            "is_writer",
            "created_at",
            "modified_at",
        )

    def get_is_writer(self, obj):
        try:
            login_user = self.context.get("login_user")
        except:
            login_user = None

        return (
            True
            if Comment.objects.filter(idx=obj.idx, writer=login_user).exists()
            else False
        )

    # noinspection PyMethodMayBeStatic
    def get_writer_avatar(self, obj):
        if not obj.writer.profile.avatar:
            return MEDIA_URL + "default_avatar.png"
        return MEDIA_URL + str(obj.writer.profile.avatar)


class PostDisplayDetailSerializer(serializers.ModelSerializer):
    writer = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    writer_avatar = serializers.SerializerMethodField()
    hashtag = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    is_login_user_liked = serializers.SerializerMethodField()
    is_writer = serializers.SerializerMethodField()
    writer_other_post = serializers.SerializerMethodField()
    is_login_user_follow = serializers.SerializerMethodField()
    is_login_user_bookmark = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "idx",
            "writer",
            "writer_avatar",
            "title",
            "image",
            "content",
            "ref_url",
            "views",
            "likes",
            "is_login_user_liked",
            "is_login_user_bookmark",
            "is_login_user_follow",
            "is_writer",
            "topic",
            "week",
            "is_muse",
            "created_at",
            "modified_at",
            "hashtag",
            "comment",
            "writer_other_post",
        )

    def get_is_login_user_bookmark(self, obj):
        try:
            login_user = self.context.get("request").user
        except:
            login_user = None
        return (
            True
            if PostBookmark.objects.filter(post=obj, user=login_user).exists()
            else False
        )

    def get_is_login_user_liked(self, obj):
        try:
            login_user = self.context.get("request").user
        except:
            login_user = None
        return (
            True
            if PostLike.objects.filter(post=obj, like_user=login_user).exists()
            else False
        )

    def get_is_login_user_follow(self, obj):
        try:
            login_user = self.context.get("request").user
        except:
            login_user = None
        if Follow.objects.filter(following=login_user, follower=obj.writer).exists():
            is_followed = True
        else:
            is_followed = False
        return is_followed

    def get_writer_other_post(self, obj):
        try:
            login_user = self.context.get("request")
            post_obj = (
                Post.objects.filter(writer=obj.writer)
                .exclude(idx=obj.idx)
                .order_by("-likes", "-views")
            )
            # print(post_obj)
            if post_obj.exists():
                count_post = post_obj.count()
                if count_post >= 3:
                    post_obj = post_obj[:3]
                elif 1 <= count_post < 3:
                    post_obj = post_obj[:count_post]
                srl = PostDisplayAllSerializer(
                    post_obj, context={"request": login_user}, many=True
                )
            return srl.data
        except:
            return None

    # noinspection PyMethodMayBeStatic
    def get_writer_avatar(self, obj):
        if not obj.writer.profile.avatar:
            return MEDIA_URL + "default_avatar.png"
        return MEDIA_URL + str(obj.writer.profile.avatar)

    # noinspection PyMethodMayBeStatic
    def get_hashtag(self, obj):
        return list(obj.hashtag.names())

    def get_comment(self, obj):
        comment_obj = Comment.objects.filter(post=obj.idx)
        try:
            login_user = self.context.get("request").user
        except:
            login_user = None
        comment_serialized = CommentDisplaySerializer(
            comment_obj, context={"login_user": login_user}, many=True
        )
        return comment_serialized.data

    def get_is_writer(self, obj):
        try:
            login_user = self.context.get("request").user
        except:
            login_user = None
        return (
            True
            if Post.objects.filter(idx=obj.idx, writer=login_user).exists()
            else False
        )


class CommentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
