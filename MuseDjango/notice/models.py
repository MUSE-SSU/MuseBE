from django.db import models

# Create your models here.

NOTICE_CATEGORY = (
    ("tos", "이용 약관"),
    ("guide", "이용 안내"),
    ("general", "일반")("footer", "사이트 설명"),
)
BANNER_CATEGORY = (
    ("main_banner", "메인 배너"),
    ("muse_banner", "뮤즈 배너"),
    ("contest_banner", "콘테스트 배너"),
    ("reference_banner", "레퍼런스 배너"),
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
        verbose_name_plural = "공지사항"


class Banner(models.Model):
    idx = models.AutoField(primary_key=True, blank=False, null=False)
    category = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=BANNER_CATEGORY,
        verbose_name="배너 카테고리",
    )
    title = models.CharField(max_length=1000, blank=True, null=True, verbose_name="제목")
    content = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name="내용"
    )
    usage = models.BooleanField(default=True, verbose_name="노출 여부")
    created_at = models.DateTimeField(verbose_name="최초 업로드 날짜", auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name="최근 수정 날짜", auto_now=True)

    class Meta:
        db_table = "Banner"
        verbose_name_plural = "배너"
