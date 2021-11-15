from django.urls import path
from . import views


urlpatterns = [
    path("upload/", views.upload_topic, name="upload_topic"),
    path("display/", views.display_topic, name="display_topic"),
]
