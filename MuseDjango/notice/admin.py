from django.contrib import admin
from .models import *


class NoticeAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "banner_main",
        "banner_muse",
        "banner_contest",
        "banner_reference",
        "tos",
        "created_at",
        "modified_at",
    ]


admin.site.register(Notice, NoticeAdmin)
