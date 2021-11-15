from django.urls import path
from . import views


urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("info/", views.get_user_info, name="get-user-info"),
    path("check/nickname/", views.check_nickname_overlap, name="check-nickname-overlap"),
    path("update/", views.update_userinfo, name="update-userinfo"),
    path("follow/", views.follow, name="follow"),
    path("my-page/<str:nickname>/", views.my_page, name="my-page"),
    path("my-page/owner/<str:nickname>/", views.my_page_owner, name="my-page-owner"),
    # path("update/nickname/", views.update_nickname, name="update_nickname"),
    # path("update/avatar/", views.update_avatar, name="update_avatar"),
    # path("following-list/", views.following_list, name="following-list"),
    # path("follower-list/", views.follower_list, name="follower-list"),

]
