'''
from celery import Celery
import datetime
from datetime import timedelta
from django.db.models import F, Q, Count, Max
from models import Post

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')


@app.task(name="select_muse", bind=True, default_retry_delay=300, max_retries=5)
def select_muse():
    # 뮤즈 선정
    # 좋아요 가장 많이 받은 게시물, 동점의 경우, 조회수 더 많은 게시물
    muse_post = Post.objects.filter(cur_status=True).order_by('-likes', '-views').first()
    muse_post.is_muse = True

    # 뮤즈 선정된 유저 뱃지 증가
    muse_post.writer.profile.badge += 1

    # 게시물 현재 진행 상태 변경
    before_post = Post.objects.filter(cur_status=True)
    for i in before_post:
        i.cur_status = False
        i.save()


'''