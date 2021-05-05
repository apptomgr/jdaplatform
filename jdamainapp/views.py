from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required

@login_required
def jdamainapp_home(request):
    context ={'hello': _('hello')}
    return render(request, 'jdamainapp/jdamainapp_home.html', context)
    #return render(request, 'jdamainapp/base_bk.html')
