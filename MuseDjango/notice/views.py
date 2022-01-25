from .models import *
from .serializers import *
from rest_framework import status, viewsets
import json
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status, viewsets
from common.authentication import (
    authorization_validator,
    authorization_validator_or_none,
    MUSEAuthenticationForWeb,
)


class NoticeViewSet(viewsets.ModelViewSet):
    """공지사항 API"""

    authentication_classes = [MUSEAuthenticationForWeb]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        # GET host/api/notice/?type=
        try:
            notice_type = request.query_params.get("type", None)
        except:
            return Response({"message": "ERROR: NOTICE LIST > REQUEST"}, status=400)
        if not notice_type:
            return Response({"message": "ERROR: NOTICE LIST > REQUEST"}, status=400)

        try:
            notice_type = notice_type.split(",")
            queryset = Notice.objects.filter(
                usage=True, category__in=notice_type
            ).order_by("idx")
            serializer = NoticeSerializer(queryset, many=True)
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: NOTICE LIST"}, status=400)


class BannerViewSet(viewsets.ModelViewSet):
    """배너 API"""

    authentication_classes = [MUSEAuthenticationForWeb]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        # GET host/api/banner/?type=
        try:
            banner_type = request.query_params.get("type", None)
        except:
            return Response({"message": "ERROR: BANNER LIST > REQUEST"}, status=400)
        if not banner_type:
            return Response({"message": "ERROR: BANNER LIST > REQUEST"}, status=400)

        try:
            banner_type = banner_type.split(",")
            queryset = Banner.objects.filter(usage=True, category__in=banner_type)
            serializer = BannerSerializer(queryset, many=True)
            return Response(serializer.data, status=200)
        except:
            return Response({"message": "ERROR: BANNER LIST"}, status=400)
