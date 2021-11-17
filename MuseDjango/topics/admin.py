from django.contrib import admin
from .models import Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ["idx", "topic", "week", "activate_week"]


admin.site.register(Topic, TopicAdmin)
