from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts import views as account_views
from musepost import views as post_views


admin.site.site_header = "⚡️ Muse DB ⚡️"
admin.site.site_title = "⚡️ Muse DB ⚡️"
admin.site.index_title = "⚡️ Muse 관리 ⚡️"

router = DefaultRouter()
router.register(r"account", account_views.UserViewSet, basename="account")
router.register(r"post", post_views.PostViewSet, basename="post")
router.register(r"comment", post_views.CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    # path("accounts/", include("accounts.urls")),
    # path("posts/", include("musepost.urls")),
    path("topics/", include("topics.urls")),
]
