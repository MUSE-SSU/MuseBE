from django.shortcuts import render
import json
import requests
from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Topic


def upload_topic(request):
    if request.method == "POST":
        data = json.loads(request.body)
        topic = Topic.objects.create(topic=data["topic"], week=data["week"])
        topic.save()
        return JsonResponse({"message": "Success Upload Topic"}, status=200)


def display_topic(request):
    if request.method == "GET":
        week = request.GET.get("week", None)
        if week is None:
            return JsonResponse({"message": "No Week"}, status=400)
        else:
            if Topic.objects.filter(week=week).exists():
                topic = Topic.objects.get(week=week)
                result = {
                    "topic": topic.topic,
                    "week": topic.week,
                }
                return JsonResponse(result, status=200)
            else:
                return JsonResponse({"message": "no topic of week"}, status=400)
    else:
        return JsonResponse({"message": "wrong method"}, status=400)
