from rest_framework import serializers
from .models import *
from config.settings import MEDIA_URL
from musepost.models import Post, PostLike
from musepost.serializers import PostDisplayAllSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserInfoSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()
    self_introduce = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "nickname", "avatar", "badge", "self_introduce")

    def get_avatar(self, obj):
        if not obj.profile.avatar:
            return MEDIA_URL + "default_avatar.png"
        return MEDIA_URL + str(obj.profile.avatar)

    def get_badge(self, obj):
        return obj.profile.badge

    def get_self_introduce(self, obj):
        return obj.profile.self_introduce


"""
class UserNicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("nickname",)


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("avatar",)
"""


class FollwingSerializer(serializers.ModelSerializer):
    follower = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ("follower", "avatar")

    def get_avatar(self, obj):
        try:
            follower_user = User.objects.get(user_id=obj.follower)
        except:
            follower_user = None

        if not follower_user.profile.avatar:
            return MEDIA_URL + "default_avatar.png"
        return MEDIA_URL + str(follower_user.profile.avatar)


class FollwerSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ("following", "avatar")

    def get_avatar(self, obj):
        try:
            following_user = User.objects.get(user_id=obj.following)
        except:
            following_user = None

        if not following_user.profile.avatar:
            return MEDIA_URL + "default_avatar.png"
        return MEDIA_URL + str(following_user.profile.avatar)


class MyPageSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    # owner_post = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    follower_list = serializers.SerializerMethodField()
    following_list = serializers.SerializerMethodField()
    is_login_user_follow = serializers.SerializerMethodField()
    owner_info = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "is_owner",
            "owner_info",
            "is_login_user_follow",
            "follower_count",
            "following_count",
            "follower_list",
            "following_list",
            # "owner_post",
        )

    def get_owner_info(self, obj):
        serializer = UserInfoSerializer(obj)
        return serializer.data

    def get_is_login_user_follow(self, obj):
        request = self.context.get("request")
        if Follow.objects.filter(following=request.user, follower=obj).exists():
            is_followed = True
        else:
            is_followed = False
        return is_followed

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return True if request.user == obj else False

    # def get_owner_post(self, obj):
    #     login_user = self.context.get("request")
    #     post_obj = Post.objects.filter(writer=obj).order_by("-created_at")
    #     srl = PostDisplayAllSerializer(
    #         post_obj, context={"request": login_user}, many=True
    #     )
    #     return srl.data

    def get_follower_count(self, obj):
        return Follow.objects.filter(follower=obj).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(following=obj).count()

    def get_follower_list(self, obj):
        owner_follower = Follow.objects.filter(follower=obj)
        srl = FollwerSerializer(owner_follower, many=True)
        return srl.data

    def get_following_list(self, obj):
        owner_following = Follow.objects.filter(following=obj)
        srl = FollwingSerializer(owner_following, many=True)

        return srl.data
