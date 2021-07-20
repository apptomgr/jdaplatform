from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils import translation

def get_user_grp(request):
    grp = None
    if request.user.groups.all():
        grp = request.user.groups.all()[0].name
    return grp

@login_required
def jdamainapp_home(request):
    curr_lang_code=translation.get_language()

    grp = get_user_grp(request)
    context = {'user_grp':grp,'hello': _('hello'), 'curr_lang_code': curr_lang_code}
    return render(request, 'jdamainapp/jdamainapp_home.html', context)
    #return render(request, 'jdamainapp/base_bk.html')


@login_required
def jdamainapp_account_profile(request):
    grp = get_user_grp(request)
    context = {'user_grp':grp,'hello': _('hello')}
    return render(request, 'jdamainapp/profile.html', context)


