from django.contrib import admin
from .models import *


class NoticeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Notice._meta.get_fields()]


class BannerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Banner._meta.get_fields()]


admin.site.register(Notice, NoticeAdmin)
admin.site.register(Banner, BannerAdmin)
