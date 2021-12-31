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
from functools import reduce

# 통합 검색
@authorization_validator_or_none
def integrated_search(request):
    if request.method == "GET":
        try:
            search = request.GET.get("q", None)
            if search:
                search = search.split(" ")
                result = {}

                # 유저 닉네임 검색
                query = reduce(
                    operator.or_, (Q(nickname__icontains=key) for key in search)
                )
                user_queryset = User.objects.filter(query)
                if user_queryset:
                    user_serializer = UserInfoSerializer(user_queryset, many=True)
                    result["user"] = user_serializer.data

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
                post_queryset = Post.objects.filter(
                    Q(hashtag__name__in=search)
                    | post_title_query
                    | post_content_query
                    | post_writer_query
                ).distinct()

                if post_queryset:
                    post_serializer = PostDisplayAllSerializer(
                        post_queryset, context={"request": request}, many=True
                    )
                    result["post"] = post_serializer.data

                if result:
                    return JsonResponse(result, safe=False, status=200)
                else:
                    return JsonResponse({"message": "NO SEARCH LIST"}, status=200)
        except:
            return JsonResponse({"message": "ERROR: SEARCH"}, status=400)
    else:
        return JsonResponse({"message": "ERROR: SEARCH"})
