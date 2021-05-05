from django.shortcuts import render
from django.http import HttpResponse

def jdawebsite_home(request):
    return HttpResponse('jdawebsite')
