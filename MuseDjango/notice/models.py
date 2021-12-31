from django.db import models

# Create your models here.

NOTICE_CATEGORY = (
    ("tos", "이용 약관"),
    ("guide", "이용 안내"),
    ("general", "일반")("footer", "사이트 설명"),
)


class Notice(models.Model):
    idx = models.AutoField(primary_key=True, blank=False, null=False)
    category = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=NOTICE_CATEGORY,
        verbose_name="공지 카테고리",
    )
    title = models.CharField(max_length=1000, blank=True, null=True, verbose_name="제목")
    content = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name="내용"
    )
    usage = models.BooleanField(default=True, verbose_name="노출 여부")
    created_at = models.DateTimeField(verbose_name="최초 업로드 날짜", auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name="최근 수정 날짜", auto_now=True)

    class Meta:
        db_table = "Notice"
        verbose_name_plural = "MUSE 공지사항"
