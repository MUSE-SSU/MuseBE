from django.utils import timezone
import jwt
import json
from django.http import JsonResponse
from my_settings import (
    KAKAO_REST_KEY,
    KAKAO_LOGIN_REDIRECT_URI,
    KAKAO_REGISTER_REDIRECT_URI,
    SECRET_KEY,
    SECRET_ALGORITHM,
)
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from common.social_auth import kakao_login
from common.authentication import (
    authorization_validator,
    authorization_validator_or_none,
    MUSEAuthenticationForWeb,
)
from .serializers import *
from musepost.serializers import *


class UserViewSet(viewsets.ModelViewSet):
    """User API"""

    authentication_classed = [MUSEAuthenticationForWeb]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request):
        # POST host/account/
        """회원가입&로그인"""
        try:
            create_type = request.data.get("type", None)
            code = request.data.get("code", None)
            if not code or not create_type:
                return Response({"message": "ERROR: USER CREATE > REQUEST"}, status=400)
        except:
            return Response({"message": "ERROR: USER CREATE > REQUEST"}, status=400)
        try:
            user_id, user_name = kakao_login(code, KAKAO_REGISTER_REDIRECT_URI)
        except:
            return Response({"message": "ERROR: USER CREATE > "}, status=400)
        try:
            if create_type == "register":
                # DB에 존재하면 로그인하라고 반환.
                if User.objects.filter(user_id=user_id).exists():
                    return Response({"result": False}, status=400)

                # DB에 없으면 회원가입 후 로그인 성공
                else:
                    serializer = UserSerializer(
                        data={
                            "user_id": user_id,
                            "username": user_name,
                            "nickname": user_name,
                        },
                        partial=True,
                    )
                    if serializer.is_valid():
                        created_user = serializer.save()
                        created_profile = UserProfile.objects.create(
                            user=created_user, avatar="default_avatar.png"
                        )
                        created_profile.save()

                        encoded_token = jwt.encode(
                            {"user_id": user_id}, SECRET_KEY, algorithm=SECRET_ALGORITHM
                        )

                        return Response(
                            {"result": True, "token": encoded_token}, status=201
                        )
                    return Response(serializer.errors, status=400)
            elif create_type == "login":
                # DB에 있는 유저면, 로그인 성공
                if User.objects.filter(user_id=user_id).exists():
                    encoded_token = jwt.encode(
                        {"user_id": user_id}, SECRET_KEY, algorithm=SECRET_ALGORITHM
                    )
                    return Response(
                        {"result": True, "token": encoded_token}, status=200
                    )

                # DB에 없으면, 회원가입부터 하라고 반환
                else:
                    return Response({"result": False}, status=400)
        except:
            return Response({"message": "ERROR: USER CREATE"}, status=400)

    def list(self, request):
        # GET host/account/
        try:
            if not request.user:
                return Response({"message": "ERROR: USER RETRIEVE > NONE"}, status=400)
            serializer = UserInfoSerializer(request.user)
        except:
            return Response({"message": "ERROR: USER RETRIEVE"}, status=400)
        return Response(serializer.data, status=200)

    def partial_update(self, request, pk=None):
        # PATCH host/account/pk(nickname)/
        try:
            nickname = request.data.get("nickname", None)
            self_introduce = request.data.get("self_introduce", "")
            avatar = request.data.get("avatar", None)
        except:
            return Response({"message": "ERROR: USER UPDATE > REQUEST"}, status=400)

        try:
            if User.objects.filter(user_id=request.user, nickname=pk).exists():
                request.user.nickname = nickname
                request.user.profile.avatar = avatar
                request.user.profile.self_introduce = self_introduce

                request.user.save()
                request.user.profile.save()
                return Response({"message": "SUCCESS"}, status=200)
            else:
                return JsonResponse({"message": "ERROR: USER UPDATE"}, status=400)
        except:
            return JsonResponse({"message": "ERROR: USER UPDATE"}, status=400)

    def retrieve(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

    @action(detail=False, methods=["post"])
    def check_nickname(self, request):
        # POST host/account/check_nickname
        try:
            checking = request.data.get("nickname", None)
            if (
                User.objects.filter(nickname=checking)
                .exclude(user_id=request.user.user_id)
                .exists()
            ):
                return Response({"result": False}, status=200)
            else:
                return Response({"result": True}, status=200)
        except:
            return Response({"message": "ERROR: USER CHECK NICKNAME"}, status=400)

    @action(detail=False, methods=["post"])
    def follow(self, request):
        # POST host/account/follow/
        try:
            follower_nickname = request.data.get("follower", None)
            following_id = request.user.user_id
        except:
            return Response({"message": "ERROR: USER FOLLOW > REQUEST"}, status=400)
        try:
            if (
                User.objects.filter(nickname=follower_nickname).exists()
                and User.objects.filter(user_id=following_id).exists()
            ):
                follower = User.objects.get(nickname=follower_nickname)
                following = User.objects.get(user_id=following_id)

                if follower == following:  # 자기 자신 누르는 경우
                    return Response(
                        {"message": "ERROR: USER FOLLOW > SELF FOLLOW"}, status=400
                    )

                follows, is_followed = Follow.objects.get_or_create(
                    following=following, follower=follower
                )
                if not is_followed:
                    follows.delete()
                    result = False
                else:
                    result = True
                return Response({"message": result}, status=200)
        except:
            return Response({"message": "ERROR: USER FOLLOW"}, status=400)

    @action(detail=True, methods=["get"])
    def my_page(self, request, pk=None):
        # GET host/account/pk/my_page/
        try:
            owner = User.objects.get(nickname=pk)
            serializer = MyPageSerializer(owner, context={"request": request})
        except:
            return Response({"message": "ERROR: MY PAGE"}, status=400)
        return Response(serializer.data, status=200)

    @action(detail=True, methods=["get"])
    def owner_post(self, request, pk=None):
        # GET host/account/pk/owner_post/
        try:
            owner = User.objects.get(nickname=pk)
            owner_post = Post.objects.filter(writer=owner).order_by("-created_at")
            serializer = PostDisplayAllSerializer(
                owner_post, context={"request": request}, many=True
            )
            print(serializer.data)
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: OWNER POST"}, status=400)

    @action(detail=True, methods=["get"])
    def owner_liked_post(self, request, pk=None):
        # GET host/account/pk/owner_liked_post/
        try:
            if User.objects.get(nickname=pk) == request.user:
                owner_liked_post = Post.objects.filter(
                    post_like__like_user=request.user
                ).order_by("-created_at")
                serializer = PostDisplayAllSerializer(
                    owner_liked_post, context={"request": request}, many=True
                )
                return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: OWNER LIKED POST"}, status=400)


def register(request):
    """
    유저 회원가입
    - 디비에 있으면, 이미 존재하는 유저라고 반환.
    - 디비에 없으면, 저장 후 로그인 성공
    """
    if request.method == "POST":
        if request.META["CONTENT_TYPE"] == "application/json":
            body = json.loads(request.body)
            code = body["code"]
            if code is None:
                return JsonResponse({"message": "REQUEST ERROR"}, status=400)

            user_id, user_name = kakao_login(code, KAKAO_REGISTER_REDIRECT_URI)

            # DB에 존재하면 로그인하라고 반환.
            if User.objects.filter(user_id=user_id).exists():
                return JsonResponse(
                    {"result": False}, status=status.HTTP_400_BAD_REQUEST
                )

            # DB에 없으면 회원가입 후 로그인 성공
            else:
                serializer = UserSerializer(
                    data={
                        "user_id": user_id,
                        "username": user_name,
                        "nickname": user_name,
                    },
                    partial=True,
                )
                if serializer.is_valid():
                    created_user = serializer.save()
                    created_profile = UserProfile.objects.create(
                        user=created_user, avatar="default_avatar.png"
                    )
                    created_profile.save()

                    encoded_token = jwt.encode(
                        {"user_id": user_id}, SECRET_KEY, algorithm=SECRET_ALGORITHM
                    )
                    print(encoded_token)
                    return JsonResponse(
                        {"result": True, "token": encoded_token},
                        safe=False,
                        status=status.HTTP_201_CREATED,
                    )

                return JsonResponse(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return JsonResponse(
                {"message": "ACCESS TYPE ERROR"}, safe=False, status=400
            )
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


def login(request):
    """
    유저 로그인
    디비에 있는 유저인 지 체크
        - 없는 유저이면 로그인 실패, is_register: false 반환
        - 있는 유저이면 로그인 성공, is_register: true 반환
    """
    if request.method == "POST":
        if request.META["CONTENT_TYPE"] == "application/json":
            body = json.loads(request.body)
            code = body["code"]
            if code is None:
                return JsonResponse({"message": "REQUEST ERROR"}, status=400)

            user_id, user_name = kakao_login(code, KAKAO_LOGIN_REDIRECT_URI)

            # DB에 있는 유저면, 로그인 성공
            if User.objects.filter(user_id=user_id).exists():
                encoded_token = jwt.encode(
                    {"user_id": user_id}, SECRET_KEY, algorithm=SECRET_ALGORITHM
                )
                print(encoded_token)
                return JsonResponse(
                    {"result": True, "token": encoded_token},
                    status=status.HTTP_201_CREATED,
                )

            # DB에 없으면, 회원가입부터 하라고 반환
            else:
                return JsonResponse(
                    {"result": False}, status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return JsonResponse(
                {"message": "ACCESS TYPE ERROR"}, safe=False, status=400
            )
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def get_user_info(request):
    """
    유저 정보 반환
    """
    if request.method == "GET":
        try:
            serializer = UserInfoSerializer(request.user)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def check_nickname_overlap(request):
    """
    닉네임 중복 검사
    """
    if request.method == "POST":
        try:
            nickname = request.POST["nickname"]
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)
        try:
            if (
                User.objects.filter(nickname=nickname)
                .exclude(user_id=request.user.user_id)
                .exists()
            ):
                return JsonResponse({"result": False}, status=200)
            else:
                return JsonResponse({"result": True}, status=200)
        except:
            return JsonResponse({"message": "OVERLAP ERROR"}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def update_userinfo(request):
    """
    유저 정보 수정(nickname, avatar, self_introduce)
    """
    if request.method == "POST":
        try:
            nickname = request.POST["nickname"]
            self_introduce = request.POST["self_introduce"]
            if self_introduce is None or self_introduce == "":
                self_introduce = ""
        except:
            return JsonResponse({"message": "REQUEST ERROR"}, status=400)
        try:
            avatar = request.FILES["avatar"]
        except:
            try:
                avatar_state = request.POST["avatar_state"]
                if avatar_state == "original":
                    avatar = request.user.profile.avatar
                elif avatar_state == "delete":  # 아바타 삭제 기본 이미지
                    avatar = "default_avatar.png"
            except:
                return JsonResponse({"message": "REQUEST AVATAR ERROR"}, status=400)

        try:
            if User.objects.filter(user_id=request.user).exists():
                try:
                    if request.user.nickname != nickname:
                        request.user.nickname = nickname
                except Exception as e:
                    return JsonResponse(
                        {"message": "NICKNAME IS SAME BEFORE"}, status=400
                    )

                request.user.profile.avatar = avatar
                request.user.profile.self_introduce = self_introduce

                request.user.save()
                request.user.profile.save()
                return JsonResponse(
                    {"message": "UPDATE SUCCESS", "nickname": nickname}, status=200
                )
            else:
                return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
        except:
            return JsonResponse({"message": "UPDATE ERROR"}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def follow(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            follower_nickname = data["follower"]  # 닉네임으로 들어옴
            following_id = request.user.user_id
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
        try:
            if not User.objects.filter(nickname=follower_nickname).exists():
                return JsonResponse({"message": "INVALID USER"}, status=400)
            if not User.objects.filter(user_id=following_id).exists():
                return JsonResponse({"message": "INVALID APPROACH"}, status=400)

            follower = User.objects.get(nickname=follower_nickname)
            following = User.objects.get(user_id=following_id)

            if follower == following:  # 자기 자신 누르는 경우
                return JsonResponse({"message": "INVALID APPROACH"}, status=400)

            follows, is_followed = Follow.objects.get_or_create(
                following=following, follower=follower
            )
            if not is_followed:
                follows.delete()
                result = False
            else:
                result = True

            return JsonResponse({"Follow": result}, status=200)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


"""
@authorization_validator
def following_list(request):
    # 내가 누른 사람들 -> 팔로잉
    # following_id = 나, follow_id = 내가 누른 사람들
    if request.method == "GET":
        try:
            user_id = request.user.user_id
            user_following = Follow.objects.filter(following=user_id)

            serializer = FollwingSerializer(user_following, many=True)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def follower_list(request):
    # 나를 누른 사람들 -> 팔로우
    # follower_id = 나, following_id = 나를 누른 사람들
    if request.method == "GET":
        try:
            user_id = request.user.user_id
            user_follower = Follow.objects.filter(follower=user_id)
            print(user_id)
            serializer = FollwerSerializer(user_follower, many=True)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)
"""


@authorization_validator_or_none
def my_page(request, nickname):
    if request.method == "GET":
        try:
            owner = User.objects.get(nickname=nickname)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
        try:
            serializer = MyPageSerializer(owner, context={"request": request})
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator_or_none
def owner_post(request, nickname):
    if request.method == "GET":
        try:
            owner = User.objects.get(nickname=nickname)
            owner_post = Post.objects.filter(writer=owner).order_by("-created_at")
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
        try:
            serializer = PostDisplayAllSerializer(
                owner_post, context={"request": request}, many=True
            )
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def owner_liked_post(request, nickname):
    if request.method == "GET":
        try:
            owner_liked_post = Post.objects.filter(
                post_like__like_user=request.user
            ).order_by("-created_at")
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
        try:
            if User.objects.get(nickname=nickname) == request.user:

                serializer = PostDisplayAllSerializer(
                    owner_liked_post, context={"request": request}, many=True
                )
                return JsonResponse(
                    serializer.data, safe=False, status=status.HTTP_200_OK
                )
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)
