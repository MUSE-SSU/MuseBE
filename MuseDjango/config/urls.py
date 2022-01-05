from django.contrib import admin
from django.urls import path, include
from django.views.generic import base
from rest_framework.routers import DefaultRouter
from accounts import views as account_views
from musepost import views as post_views
from notice import views as notice_views
from common import apis as common_apis
from .settings import DEV

if DEV:
    admin.site.site_header = "⚡️ Muse 개발 DB ⚡️"
    admin.site.site_title = "⚡️ Muse 개발 DB ⚡️"
    admin.site.index_title = "⚡️ Muse 개발 ⚡️"
else:  # PROD
    admin.site.site_header = "⚡️ Muse 실제 DB ⚡️"
    admin.site.site_title = "⚡️ Muse 실제 DB ⚡️"
    admin.site.index_title = "⚡️ Muse 실제 ⚡️"


router = DefaultRouter()
router.register(r"account", account_views.UserViewSet, basename="account")
router.register(r"post", post_views.PostViewSet, basename="post")
router.register(r"comment", post_views.CommentViewSet, basename="comment")
router.register(r"notice", notice_views.NoticeViewSet, basename="notice")
router.register(r"banner", notice_views.BannerViewSet, basename="banner")

urlpatterns = [
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
    # path("accounts/", include("accounts.urls")),
    # path("posts/", include("musepost.urls")),
    path("api/topics/", include("topics.urls")),
    path("api/search/", common_apis.integrated_search, name="integrated-search"),
]
