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
            raw_search = request.GET.get("q", None)

            if raw_search:
                search = [key for key in raw_search.split("+") if key]
                raw_search = "".join(raw_search.split("+"))

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

                post_queryset = (
                    Post.objects.prefetch_related("post_color")
                    .filter(
                        Q(hashtag__name__in=search)
                        | post_title_query
                        | post_content_query
                        | post_writer_query
                        | Q(post_color__palette_color1__icontains=raw_search)
                        | Q(post_color__palette_color2__icontains=raw_search)
                        | Q(post_color__palette_color3__icontains=raw_search)
                        | Q(post_color__palette_color4__icontains=raw_search)
                        | Q(post_color__palette_color5__icontains=raw_search)
                    )
                    .distinct()
                )

                if post_queryset:
                    post_serializer = PostDisplayAllSerializer(
                        post_queryset, context={"request": request}, many=True
                    )
                    result["post"] = post_serializer.data
                else:
                    result["post"] = None

                # try:
                #     if request.user:
                #         search_user = request.user.nickname
                #     else:
                #         search_user = None
                # except:
                #     search_user = None

                slack_post_message(
                    MUSE_SLACK_TOKEN,
                    "#muse-dev" if DEV else "#muse-prod",
                    f"👍 유저 검색: {search}",
                )
                return JsonResponse(result, safe=False, status=200)
            else:
                return JsonResponse(
                    {"user": None, "post": None}, safe=False, status=200
                )
        except:
            return JsonResponse({"message": "ERROR: SEARCH"}, status=400)
    else:
        return JsonResponse({"message": "ERROR: SEARCH"})
