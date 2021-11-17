from django.contrib import admin
from django.urls import path, include

# from django.conf.urls.static import static
# from .settings import DEBUG, MEDIA_ROOT, MEDIA_URL

admin.site.site_header = "⚡️ Muse DB ⚡️"
admin.site.site_title = "⚡️ Muse DB ⚡️"
admin.site.index_title = "⚡️ Muse 관리 ⚡️"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("posts/", include("musepost.urls")),
    path("topics/", include("topics.urls")),
]


"""
if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
"""
