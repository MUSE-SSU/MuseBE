from re import L
from django.shortcuts import get_object_or_404
import json
import requests
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from accounts.models import User
from .models import *
from topics.models import Topic
from django.db.models import F, Q, Count, Max
import operator
from functools import reduce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status, viewsets
from common.authentication import (
    authorization_validator,
    authorization_validator_or_none,
    MUSEAuthenticationForWeb,
)
from .serializers import *
import random
from .tasks import get_image_color


class PostViewSet(viewsets.ModelViewSet):
    """Post API"""

    authentication_classes = [MUSEAuthenticationForWeb]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request):
        # POST host/post/
        try:
            upload_type = request.data.get("type", None)
            title = request.data.get("title", None)
            content = request.data.get("content", None)
            image = request.data.get("image", None)
            hashtag = request.data.get("hashtag", None)
            ref_url = request.data.get("ref_url", None)
        except:
            return Response({"message": "ERROR: POST CREATE > REQUEST"}, status=400)
        try:
            if hashtag:
                hashtag = hashtag.strip().split(" ")

            if upload_type == "reference":
                data = {
                    "writer": request.user,
                    "title": title,
                    "content": content,
                    "image": image,
                    "hashtag": hashtag,
                    "cur_status": False,
                    "category": upload_type,
                    "ref_url": ref_url,
                }

            elif upload_type == "contest":
                try:
                    cur_contest = Topic.objects.get(activate_week=True)
                    week = cur_contest.week
                    topic = cur_contest.topic
                except:
                    week = 0
                    topic = "미정"

                data = {
                    "writer": request.user,
                    "title": title,
                    "content": content,
                    "image": image,
                    "hashtag": hashtag,
                    "week": week,
                    "topic": topic,
                    "category": upload_type,
                    "cur_status": True,
                }

            serializer = PostUploadSerializer(data=data, partial=True)
            if serializer.is_valid():
                uploaded_post = serializer.save()
                # 이미지 색상 추출
                get_image_color.delay(uploaded_post.idx)

                return Response({"message": "SUCCESS"}, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "ERROR: POST CREATE"}, status=400)

    def list(self, request):
        # GET host/post/?type=reference&page=1&order_by=likes
        try:
            post_type = request.query_params.get("type", None)
            page = int(request.query_params.get("page", None))
            order_by = request.query_params.get("order", "likes")
        except:
            return Response({"message": "ERROR: POST LIST > REQUEST"}, status=400)

        if not page or not post_type:
            return Response({"message": "ERROR: POST LIST > REQUEST"}, status=400)
        try:
            if post_type == "cur-contest":
                qs = Post.objects.filter(category="contest", cur_status=True)
            elif post_type == "past-contest":
                qs = Post.objects.filter(category="contest", cur_status=False)
            elif post_type == "reference":
                qs = Post.objects.filter(category="reference")
            else:
                return Response({"message": "REQUEST ERROR"}, status=400)

            PAGE_SIZE = 8
            limit = int(page * PAGE_SIZE)
            offset = int(limit - PAGE_SIZE)

            if order_by == "recent":
                post = qs.order_by("-created_at")
            elif order_by == "views":
                post = qs.order_by("-views", "-created_at")
            else:  # Default: likes
                post = qs.order_by("-likes", "-created_at")

            count_post = post.count()

            if count_post < offset:
                return Response({"message": "POST COUNT LIMIT"}, status=201)
            elif count_post < limit:
                post_list = post[offset:count_post]
            else:
                post_list = post[offset:limit]

            serializer = PostDisplayAllSerializer(
                post_list, context={"request": request}, many=True
            )
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: POST LIST"}, status=400)

    def retrieve(self, request, pk=None):
        # GET host/post/pk
        try:
            post = Post.objects.get(idx=pk)
        except:
            return Response({"message": "ERROR: POST RETRIEVE > NONE"}, status=400)
        try:
            post.views += 1
            post.save()
            serializer = PostDisplayDetailSerializer(post, context={"request": request})
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: POST RETRIEVE"}, status=400)

    def partial_update(self, request, pk=None):
        # PATCH host/post/pk
        try:
            title = request.data.get("title", None)
            content = request.data.get("content", None)
            image = request.data.get("image", None)
            hashtag = request.data.get("hashtag", None)
            ref_url = request.data.get("ref_url", None)
        except:
            return Response({"message": "ERROR: POST UPDATE > REQUEST"}, status=400)

        if hashtag:
            hashtag = hashtag.split().split(" ")
        try:
            if Post.objects.filter(idx=pk, writer=request.user).exists():
                post = Post.objects.get(idx=pk)
                if title:
                    post.title = title
                if content:
                    post.content = content
                if image:
                    post.image = image
                if hashtag:
                    post.hashtag = hashtag
                if ref_url:
                    post.ref_url = ref_url
                post.save()
                return Response({"message": "SUCCESS"}, status=200)
        except:
            return Response({"message": "ERROR: POST UPDATE"}, status=400)

    def destroy(self, request, pk=None):
        # DELETE host/post/pk/
        try:
            if Post.objects.filter(idx=pk, writer=request.user).exists():
                post = Post.objects.get(idx=pk)
                post.delete()
        except:
            return Response({"message": "ERROR: POST DELETE"}, status=400)
        return Response({"message": "POST DELETE SUCCESS"}, status=200)

    @action(detail=False, methods=["get"])
    def preview_contest(self, request):
        # GET host/post/preview_contest
        # 현재 진행 중인 콘테스트 4개 preview
        try:
            qs = Post.objects.filter(category="contest", cur_status=True).order_by(
                "-likes", "-created_at"
            )
            POST_PREVIEW_COUNT = 4
            if qs.count() >= POST_PREVIEW_COUNT:
                post = qs[:POST_PREVIEW_COUNT]
                serializer = PostDisplayAllSerializer(
                    post, context={"request": request}, many=True
                )
            else:
                serializer = PostDisplayAllSerializer(
                    qs, context={"request": request}, many=True
                )
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: PREVIEW CONTEST"}, status=400)

    @action(detail=False, methods=["get"])
    def preview_reference(self, request):
        # GET host/post/preview_reference
        # 레퍼런스 4개 무작위 preview
        try:
            qs = list(Post.objects.filter(category="reference"))
            POST_PREVIEW_COUNT = 4
            if len(qs) > POST_PREVIEW_COUNT:
                post = random.sample(qs, POST_PREVIEW_COUNT)
                serializer = PostDisplayAllSerializer(
                    post, context={"request": request}, many=True
                )
            else:
                serializer = PostDisplayAllSerializer(
                    qs, context={"request": request}, many=True
                )
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: PREVIEW REFERENCE"}, status=400)

    @action(detail=False, methods=["get"])
    def preview_muse(self, request):
        # GET host/post/preview_muse
        try:
            cur_contest = Topic.objects.get(activate_week=True)
            past_contest_week = cur_contest.week - 1
            past_contest_muse = Post.objects.filter(
                week=past_contest_week, is_muse=True
            ).first()
            serializer = PostDisplayDetailSerializer(
                past_contest_muse, context={"request": request}
            )
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: PREVIEW MUSE"}, status=400)

    @action(detail=True, methods=["get"])
    def other_reference(self, request, pk=None):
        # GET host/post/pk/other_reference/
        pass

    @action(detail=True, methods=["get"])
    def other_contest(self, request, pk=None):
        # GET host/post/pk/other_contest/
        pass

    @action(detail=False, methods=["get"])
    def list_muse(self, request):
        # GET host/post/list_muse
        # muse 선정된 게시물, 최신 주차별로 정렬
        try:
            post = Post.objects.filter(is_muse=True).order_by("-week", "-created_at")
            serializer = PostDisplayAllSerializer(
                post, context={"request": request}, many=True
            )
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: LIST MUSE"}, status=400)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        # POST host/post/pk/like/
        try:
            post = Post.objects.get(idx=pk)
            user = User.objects.get(user_id=request.user.user_id)
            like, is_liked = PostLike.objects.get_or_create(post=post, like_user=user)
            if not is_liked:
                like.delete()
                result = False
                post.likes -= 1
            else:
                result = True
                post.likes += 1
            post.save()
            return Response({"is_like": result}, status=200)
        except:
            return Response({"message": "ERROR: POST LIKE"}, status=400)

    @action(detail=True, methods=["post"])
    def bookmark(self, request, pk=None):
        # POST host/post/pk/bookmark/
        try:
            post = Post.objects.get(idx=pk)
            user = User.objects.get(user_id=request.user.user_id)
            bookmark, is_bookmarked = PostBookmark.objects.get_or_create(
                post=post, user=user
            )
            if not is_bookmarked:
                bookmark.delete()
                result = False
            else:
                result = True
            bookmark.save()
            return Response({"is_bookmark": result}, status=200)
        except:
            return Response({"message": "ERROR: POST BOOKMARK"}, status=400)

    @action(detail=True, methods=["get"])
    def recommend_post(self, request, pk=None):
        # GET host/post/pk/recommend_post/
        # pk는 현재 보고있는 게시물의 idx
        try:
            page = int(request.query_params.get("page", 1))
            current_post = Post.objects.get(idx=pk)
        except:
            return Response({"message": "ERROR: POST BOOKMARK > REQUEST"}, status=400)
        try:
            color = [
                current_post.dominant_color,
                current_post.palette_color1,
                current_post.palette_color2,
                current_post.palette_color3,
            ]
            dominant_query = reduce(
                operator.or_, (Q(dominant_color__icontains=c) for c in color)
            )
            palette1_query = reduce(
                operator.or_, (Q(palette_color1__icontains=c) for c in color)
            )
            palette2_query = reduce(
                operator.or_, (Q(palette_color2__icontains=c) for c in color)
            )
            palette3_query = reduce(
                operator.or_, (Q(palette_color3__icontains=c) for c in color)
            )
            recommend_post = (
                Post.objects.filter(category=current_post.category)
                .exclude(idx=pk)
                .filter(
                    dominant_query | palette1_query | palette2_query | palette3_query
                )
                .distinct()
            )
        except:
            return Response({"message": "ERROR: POST RECOMMEND > RECOMMEND"}, status=400)
        try:
            PAGE_SIZE = 8
            limit = int(page * PAGE_SIZE)
            offset = int(limit - PAGE_SIZE)

            count_post = recommend_post.count()

            if count_post < offset:
                return Response({"message": "POST COUNT LIMIT"}, status=201)
            elif count_post < limit:
                post_list = recommend_post[offset:count_post]
            else:
                post_list = recommend_post[offset:limit]

            serializer = PostDisplayAllSerializer(
                post_list, context={"request": request}, many=True
            )
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: POST RECOMMEND > LIST"}, status=400)


class CommentViewSet(viewsets.ModelViewSet):

    authentication_classes = [MUSEAuthenticationForWeb]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request):
        # POST host/comment/
        try:
            comment = request.data.get("comment", None)
            post_idx = request.data.get("post_idx", None)
            if not comment or not post_idx:
                return Response(
                    {"message": "ERROR: COMMENT CREATE > REQUEST"}, status=400
                )

            data = {"post": post_idx, "writer": request.user, "comment": comment}
            serializer = CommentUploadSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "SUCCESS"}, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "ERROR: COMMENT CREATE"}, status=400)

    def destroy(self, request, pk=None):
        # DELETE host/comment/pk/
        try:
            if Comment.objects.filter(idx=pk, writer=request.user).exists():
                Comment.objects.get(idx=pk).delete()
                return Response({"message": " SUCCESS"}, status=200)
            else:
                return Response({"message": "ERROR: COMMENT DELETE > NONE"}, status=400)
        except:
            return Response({"message": "ERROR: COMMENT DELETE"}, status=401)

    def partial_update(self, request, pk=None):
        # PATCH host/comment/pk/
        try:
            comment = request.data.get("comment", None)

            if Comment.objects.filter(idx=pk, writer=request.user):
                obj = Comment.objects.get(idx=pk, writer=request.user)
                obj.comment = comment
                obj.save()
                return Response({"message": "SUCCESS"}, status=200)
            else:
                return Response({"message": "UNAUTHORIZED"}, status=401)
        except:
            return Response({"message": "REQUEST ERROR"}, status=400)


@authorization_validator
def post_reference_upload(request):
    if request.method == "POST":
        try:
            upload_type = "reference"
            ref_url = request.POST.get("ref_url", "")
            title = request.POST["title"]
            content = request.POST["content"]
            image = request.FILES["image"]
            hashtag = request.POST.get("hashtag", "").strip()
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)
        if hashtag != "":
            hashtag = hashtag.split(" ")

        if upload_type == "reference":
            data = {
                "writer": request.user,
                "title": title,
                "content": content,
                "image": image,
                "hashtag": hashtag,
                "is_contest": False,
                "cur_status": False,
                "is_reference": True,
                "ref_url": ref_url,
            }

            serializer = PostUploadSerializer(data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, safe=False, status=200)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=401)


@authorization_validator
def post_contest_upload(request):
    if request.method == "POST":
        try:
            upload_type = "contest"
            title = request.POST["title"]
            content = request.POST["content"]
            image = request.FILES["image"]
            hashtag = request.POST.get("hashtag", "").strip()
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        if hashtag != "":
            hashtag = hashtag.split(" ")

        if upload_type == "contest":
            try:
                cur_contest = Topic.objects.get(activate_week=True)
                week = cur_contest.week
                topic = cur_contest.topic
            except:
                week = 0
                topic = "미정"

            data = {
                "writer": request.user,
                "title": title,
                "content": content,
                "image": image,
                "hashtag": hashtag,
                "week": week,
                "topic": topic,
                "is_contest": True,
                "cur_status": True,
                "is_reference": False,
            }

            serializer = PostUploadSerializer(data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, safe=False, status=200)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=401)


@authorization_validator_or_none
def post_display_all(request):
    """
    게시물 보여주기
    무한스크롤: 스크롤이 끝에 닿을 때마다, 인덱스 가져와서 게시물 page_size 개수씩 반환
    정렬: 좋아요순(디폴트), 조회수순, 최신순
    """
    if request.method == "GET":
        try:
            post_type = request.GET.get("type", None)
            page = int(request.GET.get("page", None))
            order_by = request.GET.get("order", "likes")
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        if page == None or post_type == None:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        if post_type == "cur-contest":
            qs = Post.objects.filter(is_contest=True, cur_status=True)
        elif post_type == "past-contest":
            qs = Post.objects.filter(is_contest=True, cur_status=False)
        elif post_type == "reference":
            qs = Post.objects.filter(is_reference=True)
        else:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        page_size = 8
        limit = int(page * page_size)
        offset = int(limit - page_size)

        if order_by == "recent":
            post = qs.order_by("-created_at")
        elif order_by == "views":
            post = qs.order_by("-views", "-created_at")
        else:  # Default: likes
            post = qs.order_by("-likes", "-created_at")

        count_post = post.count()

        if count_post < offset:
            return JsonResponse({"message": "POST COUNT LIMIT"}, status=201)
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
        # post_view_up(post_idx)
        try:
            post = Post.objects.get(idx=post_idx)
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        serializer = PostDisplayDetailSerializer(post, context={"request": request})
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator_or_none
def post_display_contest_preview(request):
    if request.method == "GET":
        # 주차 마다 프리뷰 4개씩
        try:
            max_week = Post.objects.aggregate(Max("week"))["week__max"]
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)
        try:
            POST_PREVIEW_COUNT = 4
            # result = {"max_week": max_week}
            result = []
            while max_week:
                qs = Post.objects.filter(week=max_week).order_by("-likes", "-views")
                post = qs[:POST_PREVIEW_COUNT]
                serializer = PostDisplayAllSerializer(
                    post, context={"request": request}, many=True
                )
                # result[f"week_{max_week}"] = serializer.data
                result.append(serializer.data)
                max_week -= 1

            return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({"message": "GET POST WEEK DATA ERROR"}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator_or_none
def muse_section(request):
    if request.method == "GET":
        """
        메인: 뮤즈 섹션
        - 작가이름, 프로필사진, 작품 이미지, 좋아요개수, 조회수개수,
        """
        try:
            cur_contest = Topic.objects.get(activate_week=True)
            past_contest_week = cur_contest.week - 1
            past_contest_muse = Post.objects.filter(
                week=past_contest_week, is_muse=True
            )[0]

        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        serializer = PostDisplayDetailSerializer(
            past_contest_muse, context={"request": request}
        )
        return JsonResponse(serializer.data, safe=False, status=200)

    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator_or_none
def contest_section(request):
    if request.method == "GET":
        try:
            # 현재 진행 중인 콘테스트 작품 4개 preview
            qs = Post.objects.filter(is_contest=True, cur_status=True).order_by(
                "-likes", "-created_at"
            )
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)
        try:
            POST_PREVIEW_COUNT = 4
            if qs.count() >= POST_PREVIEW_COUNT:
                post = qs[:POST_PREVIEW_COUNT]
                serializer = PostDisplayAllSerializer(
                    post, context={"request": request}, many=True
                )
            else:
                serializer = PostDisplayAllSerializer(
                    qs, context={"request": request}, many=True
                )
            return JsonResponse(serializer.data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator_or_none
def reference_section(request):
    if request.method == "GET":
        try:
            # 레퍼런스 4개 preview
            qs = list(Post.objects.filter(is_reference=True))
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)
        try:
            POST_PREVIEW_COUNT = 4
            if len(qs) > POST_PREVIEW_COUNT:
                post = random.sample(qs, POST_PREVIEW_COUNT)
                # post = qs[:POST_PREVIEW_COUNT]
                serializer = PostDisplayAllSerializer(
                    post, context={"request": request}, many=True
                )
            else:
                serializer = PostDisplayAllSerializer(
                    qs, context={"request": request}, many=True
                )
            return JsonResponse(serializer.data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
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
            week = Post.objects.aggregate(Max("week"))["week__max"]

        if order_by == "recent":
            post = Post.objects.filter(week=week).order_by("-created_at")
        elif order_by == "views":
            post = Post.objects.filter(week=week).order_by("-views", "-created_at")
        else:  # Default: likes
            post = Post.objects.filter(week=week).order_by("-likes", "-created_at")

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
        post = Post.objects.filter(is_muse=True).order_by("-week", "-created_at")
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
            hashtag = request.POST.get("hashtag", "").strip()
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)

        if hashtag != "":
            hashtag = hashtag.split(" ")

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
                return JsonResponse(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
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
