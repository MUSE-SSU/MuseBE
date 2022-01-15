from django.http.response import HttpResponse


def index(request):
    return HttpResponse("THIS IS MUSE", status=200)
