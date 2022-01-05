from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from .models import *
from accounts.models import *
from config.settings import MEDIA_URL
from .color_constants import COLORS_TO_HEXA


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
            "category",
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


class ColorOfWeekSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()
    hexa_code = serializers.SerializerMethodField()

    class Meta:
        model = ColorOfWeek
        fields = ("color", "hexa_code")

    def get_color(self, obj):
        return [obj.color1, obj.color2, obj.color3, obj.color4, obj.color5]

    def get_hexa_code(self, obj):
        result = []
        try:
            result.append(COLORS_TO_HEXA.get(obj.color1))
        except:
            result.append("#0000ffff")
        try:
            result.append(COLORS_TO_HEXA.get(obj.color2))
        except:
            result.append("#0000ffff")
        try:
            result.append(COLORS_TO_HEXA.get(obj.color3))
        except:
            result.append("#0000ffff")
        try:
            result.append(COLORS_TO_HEXA.get(obj.color4))
        except:
            result.append("#0000ffff")
        try:
            result.append(COLORS_TO_HEXA.get(obj.color5))
        except:
            result.append("#0000ffff")
        return result
