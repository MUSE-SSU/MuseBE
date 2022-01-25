from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "user_id",
        # "username",
        "email",
        "nickname",
        "date_joined",
        "last_login",
        "is_first",
        "is_superuser",
        "is_active",
    ]


class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "get_user_id",
        "get_avatar",
        "self_introduce",
        "score",
        "badge",
        "muse",
    ]

    def get_user_id(self, obj):
        return obj.user.nickname

    def get_avatar(self, obj):
        return str(obj.avatar)

    get_user_id.short_description = "닉네임"  # Renames column head
    get_avatar.short_description = "프로필 사진"  # Renames column head
    # get_user_id.admin_order_field  = 'author'  #Allows column order sorting


class FollowAdmin(admin.ModelAdmin):
    list_display = ["get_following_nickname", "get_follower_nickname"]

    def get_following_nickname(self, obj):
        return obj.following.nickname

    def get_follower_nickname(self, obj):
        return obj.follower.nickname

    get_following_nickname.short_description = "팔로우 누른 사람"
    get_follower_nickname.short_description = "팔로우 눌린 사람"


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Follow, FollowAdmin)
