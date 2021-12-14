from django.urls import path
from . import views


urlpatterns = [
    path("upload/contest/", views.post_contest_upload, name="post_contest_upload"),
    path(
        "upload/reference/", views.post_reference_upload, name="post_reference_upload"
    ),
    path("update/<int:post_idx>/", views.post_update, name="post_update"),
    path(
        "display/all/<str:type>/<int:page>/",
        views.post_display_all,
        name="display_post_all",
    ),
    path(
        "display/detail/<int:post_idx>/",
        views.post_display_detail,
        name="display_post_detail",
    ),
    path(
        "display/preview/contest/",
        views.contest_section,
        name="display_main_contest_section",
    ),
    path(
        "display/preview/reference/",
        views.reference_section,
        name="display_main_reference_section",
    ),
    path(
        "display/contest/",
        views.post_display_contest_topic,
        name="display_post_contest_topic",
    ),
    path("display/muse/", views.post_display_muse, name="display_post_muse"),
    path("delete/<int:post_idx>/", views.post_delete, name="delete_post"),
    path("like/<int:post_idx>/", views.post_press_like, name="update_like_status"),
    path("comment/upload/<int:post_idx>/", views.comment_upload, name="upload_comment"),
    path(
        "comment/update/<int:comment_idx>/", views.comment_update, name="update_comment"
    ),
    path(
        "comment/delete/<int:comment_idx>/", views.comment_delete, name="delete_comment"
    ),
    #
]
