from django.shortcuts import get_object_or_404
import json
import requests
from django.http import JsonResponse
from rest_framework import status
from accounts.models import User
from .models import *
from topics.models import Topic
from django.db.models import F, Q, Count, Max
from rest_framework.views import APIView
from rest_framework.response import Response
from .core import authorization_validator, authorization_validator_or_none
from .serializers import *


@authorization_validator
def post_upload(request):
    """
    게시물 업로드
    """
    if request.method == "POST":
        try:
            title = request.POST["title"]
            content = request.POST["content"]
            image = request.FILES["image"]
            hashtag = request.POST.get("hashtag", '').strip()
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        if hashtag != '':
            hashtag = hashtag.split(' ')

        try:
            cur_contest = Topic.objects.get(activate_week=True)
            week = cur_contest.week
            topic = cur_contest.topic
        except:
            week = 0
            topic = '미정'

        data = {
            "writer": request.user,
            "title": title,
            "content": content,
            "image": image,
            "hashtag": hashtag,
            "week": week,
            "topic": topic,
        }

        serializer = PostUploadSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False, status=200)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=401)


@authorization_validator_or_none
def post_display_all(request, page):
    """
    게시물 보여주기
    무한스크롤: 스크롤이 끝에 닿을 때마다, 인덱스 가져와서 게시물 page_size 개수씩 반환
    정렬: 좋아요순(디폴트), 조회수순, 최신순
    """
    if request.method == "GET":
        if page is None:
            page = 1
        try:
            order_by = request.GET.get("order", "likes")
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        page_size = 6
        limit = int(page * page_size)
        offset = int(limit - page_size)

        if order_by == "recent":
            post = Post.objects.all().order_by('-created_at')
        elif order_by == "views":
            post = Post.objects.order_by('-views', '-created_at')
        else:   # Default: likes
            post = Post.objects.order_by('-likes', '-created_at')

        count_post = post.count()

        if count_post < offset:
            print("!!!! Post Count Limit !!!! ")
            return JsonResponse({"message": "POST COUNT LIMIT"}, status=400)
        elif count_post < limit:
            post_list = post[offset:count_post]
        else:
            post_list = post[offset:limit]

        serializer = PostDisplayAllSerializer(
            post_list, context={"request": request}, many=True
        )
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator_or_none
def post_display_detail(request, post_idx):
    """
    개별 포스트 정보 & 댓글 & 좋아요 누른 사람들에 속하는 지
    """
    if request.method == "GET":
        # 조회수 증가
        post_view_up(post_idx)
        try:
            post = Post.objects.get(idx=post_idx)
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        serializer = PostDisplayDetailSerializer(post, context={"request": request})
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator_or_none
def post_display_contest_topic(request):
    if request.method == "GET":
        try:
            week = request.GET.get("week", None)
            order_by = request.GET.get("order", "likes")
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        if week is None:
            week = Post.objects.aggregate(Max('week'))['week__max']

        if order_by == "recent":
            post = Post.objects.filter(week=week).order_by('-created_at')
        elif order_by == "views":
            post = Post.objects.filter(week=week).order_by('-views', '-created_at')
        else:   # Default: likes
            post = Post.objects.filter(week=week).order_by('-likes', '-created_at')

        serializer = PostDisplayAllSerializer(
            post, context={"request": request}, many=True
        )
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator_or_none
def post_display_muse(request):
    if request.method == "GET":
        # muse 선정된 게시물, 최신 주차별로 정렬
        post = Post.objects.filter(is_muse=True).order_by('-week', '-created_at')
        serializer = PostDisplayAllSerializer(
            post, context={"request": request}, many=True
        )
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def post_update(request, post_idx):
    if request.method == "POST":
        try:
            title = request.POST["title"]
            content = request.POST["content"]
            # image = request.FILES["image"]
            hashtag = request.POST.get("hashtag", '').strip()
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        if hashtag != '':
            hashtag = hashtag.split(' ')

        try:
            if Post.objects.filter(idx=post_idx, writer=request.user).exists():
                post = Post.objects.get(idx=post_idx, writer=request.user)
                data = {
                    "title": title,
                    "content": content,
                    # "image": image,
                    "hashtag": hashtag,
                }
                serializer = PostUploadSerializer(post, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, safe=False, status=200)
                return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"message": "UNAUTHORIZED"}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def post_delete(request, post_idx):
    if request.method == "DELETE":
        try:
            if Post.objects.filter(idx=post_idx, writer=request.user).exists():
                Post.objects.get(idx=post_idx).delete()
        except:
            return JsonResponse({"message": "UNAUTHORIZED"}, status=400)
        return JsonResponse({"message": "DELETE SUCCESS"}, status=200)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


def post_view_up(post_id):
    post = get_object_or_404(Post, idx=post_id)
    post.views += 1
    post.save()


@authorization_validator
def post_press_like(request, post_idx):
    if request.method == "POST":
        try:
            post = Post.objects.get(idx=post_idx)
            user = User.objects.get(user_id=request.user.user_id)
        except:
            return JsonResponse({"message": "UNAUTORIZED"}, status=401)

        like, is_liked = PostLike.objects.get_or_create(post=post, like_user=user)
        if not is_liked:
            like.delete()
            result = False
            post.likes -= 1
            post.save()
        else:
            result = True
            post.likes += 1
            post.save()

        return JsonResponse({"is_press_like": result}, status=200)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def comment_upload(request, post_idx):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            comment = body["comment"]
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        data = {"post": post_idx, "writer": request.user, "comment": comment}

        serializer = CommentUploadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False, status=200)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def comment_update(request, comment_idx):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            comment = body["comment"]
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)
        if Comment.objects.filter(idx=comment_idx, writer=request.user):
            comment_obj = Comment.objects.get(idx=comment_idx, writer=request.user)
            data = {"comment": comment}

            serializer = CommentUploadSerializer(comment_obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, safe=False, status=200)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def comment_delete(request, comment_idx):
    if request.method == "DELETE":
        try:
            if Comment.objects.filter(idx=comment_idx, writer=request.user).exists():
                Comment.objects.get(idx=comment_idx).delete()
        except:
            return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
        return JsonResponse({"message": "DELETE SUCCESS"}, status=200)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


"""
# 댓글 디스플레이 => 게시물 디테일 디스플레이랑 합쳤음.
def comment_display(request, post_idx):
    if request.method == "GET":
        try:
            post = Post.objects.get(idx=post_idx)
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=401)

        if Comment.objects.filter(post=post).exists():
            comment_list = Comment.objects.filter(post=post)
            comments_serialize = CommentDisplaySerializer(comment_list, many=True)
            return JsonResponse(comments_serialize.data, safe=False, status=200)
        else:
            return JsonResponse({"message": "No Comments"}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)
"""
