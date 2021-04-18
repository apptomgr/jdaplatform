from django.shortcuts import render
from django.http import HttpResponse

def jdaanalyticsapp_home(request):

    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_home.html')
