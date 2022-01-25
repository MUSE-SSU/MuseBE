from django.http import JsonResponse
import json
import requests
from my_settings import KAKAO_REST_KEY, SECRET_KEY, SECRET_ALGORITHM
from rest_framework.response import Response


def kakao_login(code, log_method):
    # Get Access Token
    try:
        response = requests.get(
            "https://kauth.kakao.com/oauth/token",
            params={
                "grant_type": "authorization_code",
                "client_id": KAKAO_REST_KEY,
                "redirect_uri": log_method,
                "code": code,
            },
        )
    except Exception as e:
        return Response({"message": e}, status=400)

    access_token = json.loads(response.content).get("access_token")
    if access_token is None:
        return Response({"message": "INVALID CODE"}, status=400)

    # Get User Info
    try:
        response = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    except Exception as e:
        return Response({"message": e}, status=400)

    user_info = json.loads(response.content)
    if user_info.get("id") is None:
        return Response({"message": "INVALID TOKEN"}, status=400)

    user_id = user_info["id"]
    user_name = user_info["properties"]["nickname"]
    # user_email = user_info["properties"]["email"] 아마도

    return user_id, user_name
