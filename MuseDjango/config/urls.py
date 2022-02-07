from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts import views as account_views
from musepost import views as post_views
from notice import views as notice_views
from notification import views as notification_views
from common import search as search_views
from common import health_check
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
router.register(
    r"notification", notification_views.NotificationViewSet, basename="notification"
)

urlpatterns = [
    path("", health_check.index, name="health-check-home"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/topics/", include("topics.urls")),
    path("api/search/", search_views.integrated_search, name="integrated-search"),
]

# path("accounts/", include("accounts.urls")),
# path("posts/", include("musepost.urls")),
