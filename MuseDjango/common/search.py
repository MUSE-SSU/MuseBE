from accounts.models import User
from accounts.serializers import UserInfoSerializer
from musepost.models import Post
from musepost.serializers import PostDisplayAllSerializer
from common.authentication import authorization_validator_or_none
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Q
import operator
from config.settings import MUSE_SLACK_TOKEN, DEV
from common.slack_api import slack_post_message
from functools import reduce

# 통합 검색
@authorization_validator_or_none
def integrated_search(request):
    if request.method == "GET":
        try:
            search = request.GET.get("q", None)

            if search:
                search = [key for key in search.split("+") if key]
                for s in search:
                    if s == "gray" or s == "Gray":
                        search.append("grey")
                        break
                result = {}

                # 유저 닉네임 검색
                query = reduce(
                    operator.or_, (Q(nickname__icontains=key) for key in search)
                )
                user_queryset = User.objects.filter(query)
                if user_queryset:
                    user_serializer = UserInfoSerializer(user_queryset, many=True)
                    result["user"] = user_serializer.data
                else:
                    result["user"] = None

                # 게시물 검색
                post_title_query = reduce(
                    operator.or_, (Q(title__icontains=key) for key in search)
                )
                post_content_query = reduce(
                    operator.or_, (Q(content__icontains=key) for key in search)
                )
                post_writer_query = reduce(
                    operator.or_, (Q(writer__nickname__icontains=key) for key in search)
                )
                post_color_query = reduce(
                    operator.or_, (Q(dominant_color__icontains=key) for key in search)
                )
                post_queryset = Post.objects.filter(
                    Q(hashtag__name__in=search)
                    | post_title_query
                    | post_content_query
                    | post_writer_query
                    | post_color_query
                ).distinct()

                if post_queryset:
                    post_serializer = PostDisplayAllSerializer(
                        post_queryset, context={"request": request}, many=True
                    )
                    result["post"] = post_serializer.data
                else:
                    result["post"] = None

                
                try:
                    search_user = request.user.nickname
                except:
                    search_user = None
                slack_post_message(
                    MUSE_SLACK_TOKEN,
                    "#muse-dev" if DEV else "#muse-prod",
                    f"👍 검색: {search}, 유저: {search_user}",
                )
                return JsonResponse(result, safe=False, status=200)
        except:
            return JsonResponse({"message": "ERROR: SEARCH"}, status=400)
    else:
        return JsonResponse({"message": "ERROR: SEARCH"})
