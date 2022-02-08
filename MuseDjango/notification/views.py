from .models import *
from .serializers import *
from config.settings import MEDIA_URL, MUSE_SLACK_TOKEN, DEV
from common.slack_api import slack_post_message
from common.authentication import MUSEAuthenticationForWeb
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated


class NotificationViewSet(viewsets.ModelViewSet):
    authentication_classes = [MUSEAuthenticationForWeb]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            # 읽은 알림, 안읽은 알림 모두 전달 -> 프론트에서 다르게 표현
            noti = Notification.objects.filter(user=request.user).order_by("-id")
            serializer = NotificationSerializer(noti, many=True)
            noti.update(is_read=True)

            return Response(serializer.data, status=200)
        except:
            return Response({"message": "NOTI ERROR"}, status=400)
