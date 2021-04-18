from django.shortcuts import render
from django.http import HttpResponse

def jdamainapp_home(request):
    return render(request, 'jdamainapp/jdamainapp_home.html')
    #return render(request, 'jdamainapp/base_bk.html')
