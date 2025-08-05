from django.http import HttpResponse


def index(request):
    return HttpResponse("Back-office homepage is working.")
