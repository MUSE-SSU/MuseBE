from django import db
from django.db import models
from accounts.models import User
from .utils import upload_post_image

# from topics.models import Topic
from config.asset_storage import PublicMediaStorage
from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase


# 업로드 게시물(작품)
class Post(models.Model):
    idx = models.AutoField(primary_key=True, null=False, blank=False)
    writer = models.ForeignKey(
        User,
        to_field="user_id",
        on_delete=models.CASCADE,
        related_name="post",
        verbose_name="작성자",
    )

    # 본문 content
    title = models.CharField(max_length=100, verbose_name="제목")
    image = models.ImageField(
        upload_to=upload_post_image, storage=PublicMediaStorage(), verbose_name="작품"
    )
    content = models.TextField(max_length=300, verbose_name="내용")

    views = models.PositiveIntegerField(default=0, verbose_name="조회수")
    likes = models.PositiveIntegerField(default=0, verbose_name="좋아요")
    topic = models.CharField(max_length=128, verbose_name="주제", null=True, blank=True)
    week = models.IntegerField(default=0, verbose_name="해당 주차", null=True, blank=True)
    hashtag = TaggableManager(blank=True)

    # 콘테스트 참가 여부 / 현재 상태 / 뮤즈 선정
    is_contest = models.BooleanField(default=True, verbose_name="콘테스트 참가 여부")
    cur_status = models.BooleanField(default=True, verbose_name="현재 진행 여부")
    is_muse = models.BooleanField(default=False, verbose_name="MUSE 선정 여부")

    created_at = models.DateTimeField(verbose_name="최초 업로드 날짜", auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name="최근 수정 날짜", auto_now=True)

    class Meta:
        db_table = "Post"
        verbose_name_plural = "게시글"

    def __str__(self):
        return str(self.idx)


class PostLike(models.Model):
    idx = models.AutoField(primary_key=True, null=False, blank=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        db_column="post_idx",
        related_name="post_like",
        verbose_name="게시글",
    )

    like_user = models.ForeignKey(
        User,
        to_field="user_id",
        on_delete=models.CASCADE,
        db_column="like_user",
        related_name="likeUser",
        verbose_name="좋아요 누른 유저",
    )

    class Meta:
        db_table = "Post_Like"
        verbose_name_plural = "게시글 좋아요"


# 댓글
class Comment(models.Model):
    # 해당 게시물
    idx = models.AutoField(primary_key=True, null=False, blank=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        db_column="post_idx",
        related_name="comment",
        verbose_name="게시글",
    )
    writer = models.ForeignKey(
        User,
        to_field="user_id",
        on_delete=models.CASCADE,
        db_column="writer_id",
        related_name="comment",
        verbose_name="작성자",
    )

    comment = models.CharField(max_length=128, verbose_name="댓글", default="None")
    created_at = models.DateTimeField(verbose_name="최초 업로드 날짜", auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name="최근 수정 날짜", auto_now=True)

    def get_post_id(self):
        return str(self.post)

    def get_writer_id(self):
        return str(self.writer)

    class Meta:
        db_table = "Post_Comments"
        verbose_name_plural = "댓글"
