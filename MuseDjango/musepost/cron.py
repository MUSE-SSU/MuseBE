from .models import Post
from topics.models import Topic


def crontab_test():
    print("hellooodododo")


def select_muse():
    try:
        # 뮤즈 선정
        # 좋아요 가장 많이 받은 게시물, 동점의 경우, 조회수 더 많은 게시물
        muse_post = Post.objects.filter(cur_status=True).order_by('-likes', '-views').first()
        muse_post.is_muse = True
        # 뮤즈 선정된 유저 뱃지 증가
        muse_post.writer.profile.badge += 1
        muse_post.save()
        muse_post.writer.profile.save()
    except:
        print("Error Select Muse")
    try:
        # 게시물 현재 진행 상태 변경
        before_post = Post.objects.filter(cur_status=True)
        for i in before_post:
            i.cur_status = False
            i.save()
    except:
        print("Error Current Status")
    try:
        # 주차와 주제 활성 상태 변경
        before_topic = Topic.objects.get(activate_week=True)
        before_topic.activate_week = False
        before_topic.save()

        before_week = before_topic.week
        now_week = before_week + 1
        now_topic = Topic.objects.get(week=now_week)
        now_topic.activate_week = True
        now_topic.save()
    except:
        print("Error Topic Status")


def get_rank():
    try:
        BADGE_SCORE=1000
        LIKES_SCORE=1
        VIEWS_SCORE=0.2
        post_qs = Post.objects.values('is_muse', 'likes', 'views')
        rank = []
        for post in post_qs:
            badge_score = post.is_muse * BADGE_SCORE
            likes_score = post.likes * LIKES_SCORE
            views_score = post.views * VIEWS_SCORE
            rank.append(badge_score+likes_score+views_score)
        