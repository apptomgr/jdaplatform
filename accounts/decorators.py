from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kargs):
            #print(f'7 - Working allowed roles are: {allowed_roles}')
            #print(f"8 - curr user: {request.user}- grp: {request.user.groups.all()}")
            grp =None
            if request.user.groups.exists():
                grp = request.user.groups.all()[0].name
                #print(f"11 - grp: {grp}")
            if grp in allowed_roles:
                #print(f"13 -grp: {grp}")
                return view_func(request, *args, **kargs)
            else:
                #print(f"16 - grp: {grp}")
                msg =_('you are not authorized to access this page. Would you like to login to a different account?')
                messages.info(request, f" '{request.user}' {msg} ")
                #return redirect('jdafinancialsapp_bal_rpt', sector, company.id, statement, entry_date)
                return redirect('jdapublicationsapp_home')
                #return HttpResponse('Not allowed here')
        return wrapper_func
    return decorator

#{res}, mais vous n’êtes pas autorisé à accéder à cette page. Souhaitez-vous vous connecter avec un autre compte utilisateur ?
#{res}, you are not authorized to access this page. Would you like to login to a different account?