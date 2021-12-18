from django.urls import path
from . import views


urlpatterns = [
    path("upload/contest/", views.post_contest_upload, name="post-contest-upload"),
    path(
        "upload/reference/", views.post_reference_upload, name="post-reference-upload"
    ),
    path("update/<int:post_idx>/", views.post_update, name="post-update"),
    path(
        "display/all/",
        views.post_display_all,
        name="display-post-all-by-type",
    ),
    path(
        "display/detail/<int:post_idx>/",
        views.post_display_detail,
        name="display-post-detail",
    ),
    path("display/preview/muse/", views.muse_section, name="display-main-muse-section"),
    path(
        "display/preview/contest/",
        views.contest_section,
        name="display-main-contest-section",
    ),
    path(
        "display/preview/reference/",
        views.reference_section,
        name="display-main-reference-section",
    ),
    path(
        "display/contest/",
        views.post_display_contest_topic,
        name="display-post-contest-topic",
    ),
    path("display/muse/", views.post_display_muse, name="display-post-muse"),
    path("delete/<int:post_idx>/", views.post_delete, name="delete-post"),
    path("like/<int:post_idx>/", views.post_press_like, name="update-like-status"),
    path("comment/upload/<int:post_idx>/", views.comment_upload, name="upload-comment"),
    path(
        "comment/update/<int:comment_idx>/", views.comment_update, name="update-comment"
    ),
    path(
        "comment/delete/<int:comment_idx>/", views.comment_delete, name="delete-comment"
    ),
    #
]
