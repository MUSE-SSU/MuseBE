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
from rest_framework import status
from .models import User, UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from common.social_auth import kakao_login
from common.authentication import (
    authorization_validator,
    authorization_validator_or_none,
)
from .serializers import *
from musepost.models import PostLike
from musepost.serializers import *


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
            serializer = UserInfoSerializer(request.user, context={"request": request})
        except Exception as e:
            return JsonResponse({"message": e}, status=400)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


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


'''
@authorization_validator
def update_nickname(request):
    """
    유저 닉네임 변경
    """
    if request.method == "POST":
        serializer = UserNicknameSerializer(request.user, data=json.loads(request.body))
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)


@authorization_validator
def update_avatar(request):
    """
    프사 업로드/업데이트
    """
    if request.method == "POST":
        serializer = AvatarSerializer(request.user.profile, data=request.FILES)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=400)
    else:
        return JsonResponse({"message": "ACCESS METHOD ERROR"}, status=400)
'''


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
