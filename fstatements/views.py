from django.shortcuts import render, HttpResponse


def smoke(request):
    return HttpResponse('hello')
