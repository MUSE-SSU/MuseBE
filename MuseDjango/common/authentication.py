import jwt
import requests
import json
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import User
from django.http import JsonResponse
from my_settings import SECRET_KEY, SECRET_ALGORITHM
from rest_framework import authentication, exceptions


class MUSEAuthenticationForWeb(authentication.BaseAuthentication):
    def authenticate(self, request):
        if "Authorization" not in request.headers:
            return None
        else:
            try:
                auth_header = request.headers.get("Authorization", None)
                payload = jwt.decode(
                    auth_header, SECRET_KEY, algorithms=SECRET_ALGORITHM
                )
                user_id = payload["user_id"]
                login_user = User.objects.get(user_id=user_id)

                return (login_user, None)

            except jwt.exceptions.DecodeError:
                return JsonResponse({"message": "INVALID_TOKEN"}, status=401)
            except User.DoesNotExist:
                return JsonResponse({"message": "INVALID_USER"}, status=400)


def authorization_validator(func):
    def wrapper(request, **kwargs):
        if "Authorization" not in request.headers:
            return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
        try:
            auth_header = request.headers.get("Authorization", None)
            payload = jwt.decode(auth_header, SECRET_KEY, algorithms=SECRET_ALGORITHM)
            user_id = payload["user_id"]
            login_user = User.objects.get(user_id=user_id)
            request.user = login_user
        except jwt.exceptions.DecodeError:
            return JsonResponse({"message": "INVALID_TOKEN"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"message": "INVALID_USER"}, status=400)

        return func(request, **kwargs)

    return wrapper


def authorization_validator_or_none(func):
    def wrapper(request, **kwargs):
        # 디테일은 뷰 로직에서 따로 처리해야 함.
        if "Authorization" not in request.headers:
            request.user = None
        else:
            try:
                auth_header = request.headers.get("Authorization", None)
                payload = jwt.decode(
                    auth_header, SECRET_KEY, algorithms=SECRET_ALGORITHM
                )
                user_id = payload["user_id"]
                login_user = User.objects.get(user_id=user_id)
                request.user = login_user
            except jwt.exceptions.DecodeError:
                return JsonResponse({"message": "INVALID_TOKEN"}, status=401)
            except User.DoesNotExist:
                return JsonResponse({"message": "INVALID_USER"}, status=400)

        return func(request, **kwargs)

    return wrapper
