from celery import shared_task
from .models import Post
import datetime


@shared_task
def print_hello():
    a = Post.objects.get(idx=178)
    a.content = "str(datetime.datetime.now())"
    a.save()
    print("print hello world!!!")


@shared_task
def select_muse():
    # 뮤즈 선정
    # 좋아요 가장 많이 받은 게시물, 동점의 경우, 조회수 더 많은 게시물
    contest_post = Post.objects.filter(is_contest=True, cur_status=True)
    muse_post = contest_post.order_by("-likes", "-views").first()
    muse_post.is_muse = True
    # 뮤즈 선정된 유저 뱃지 증가
    muse_post.writer.profile.badge += 1
    muse_post.save()

    # 게시물 현재 진행 상태 변경
    for i in contest_post:
        i.cur_status = False
        i.save()
