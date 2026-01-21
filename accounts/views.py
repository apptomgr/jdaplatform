from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, AccountAdminForm, AccountAdminUpdateForm, GroupUpdateForm, GroupAddForm
from django.contrib.auth.models import User
# from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from accounts .decorators import allowed_users
from datetime import datetime
from django.db.models import Count
from django.http import HttpResponseBadRequest
#from .models import SubscriptionPlan



# update registration
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add new created user to a default group
            #print(f"35 - Fresh user: {user}")
            customer_grp = Group.objects.get(name='customers') # get default grp, customers in this case
            #print(f"37:{customer_grp}")
            # Add fresh user to customer grp
            customer_grp.user_set.add(user)
            #username = form.cleaned_data.get('username')
            auth_login(request, user)
            messages.success(request, f'Your account has been successfully created. Please contact JDA to activate your account!')
            return redirect('jdamainapp_home')
            #messages.success(request, f'Your account has been created! You are now able to log in')
            #return redirect('login')
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


# profile
@login_required
def profile(request):
    #print(f'58: {request.user.password}')
    #user=request.username
    #u_form = UserUpdateForm(instance=request.user)
    #p_form = ProfileUpdateForm(instance=request.user.profile)
    user_profile = User.objects.all().select_related('profile')
    #print(user_profile) #.group.name)
    grp =None

    #print(f'65: {request.user.groups.all}')

    if request.user.groups.all():
        grp = request.user.groups.all()[0].name
        #print(f"48 - grp: {grp}")

    context = {'user_grp': grp}
    return render(request, 'registration/profile.html', context)


# profile edit
@login_required
@allowed_users(allowed_roles=['admins'])
def profile_edit(request):
    curr_grp = None
    if request.user.groups.all():
        curr_grp = request.user.groups.all()[0].name
        # print(f"98 - grp: {grp}")
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            # Now assoc watermark with the updated logo

            messages.success(request, f'Your account profile has been updated!')
            return redirect('profile')  # Redirect back to profile page

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)


    context = {'u_form': u_form,'p_form': p_form, 'user_grp': curr_grp}

    return render(request, 'registration/profile_edit.html', context)


# Account admin
@login_required
@allowed_users(allowed_roles=['admins','managers'])
def account_admin(request):
    now = datetime.now()
    curr_grp = None
    if request.user.groups.all():
        curr_grp = request.user.groups.all()[0].name

    if request.method == 'POST':
        form = AccountAdminForm(request.POST) #, instance=request.user)
        if form.is_valid():
            #Choices are: date_joined, email, first_name, groups, id, is_active, is_staff, is_superuser, last_login, last_name, logentry, password, profile, publicationmodel, user, user_permissions, username
            user=form.cleaned_data['username']
            user_info = User.objects.all().select_related('profile').filter(username=user)
            email = user_info.first().email
            grp = User.objects.values_list('groups__name', flat='True').filter(username=user).first()
            logo= user_info.first().profile.logo

            #print(f"user:{user_info} - email:{email} - Grp: {grp} - logo: {logo}")

            form = AccountAdminUpdateForm(request.POST or None, initial ={'user':user_info.first().username,'email':email,'group': grp, 'logo':logo})

            messages.success(request, f'Saved Lorem Ipsom Your account profile has been updated!')
            context={'form':form,'user':user,'email':email,'grp':grp,'logo':logo, 'rpt_date':now}
            return render(request, 'registration/account_admin_update.html', context)
        #else:
        #    messages.error(request, f'Lorem Ipsom select a user before proceeding!')
        #    return redirect('account_admin')  # Redirect back to account_admin page

    else:
        form = AccountAdminForm()
        #p_form = ProfileUpdateForm(instance=request.user.profile)


    context ={'form':form, 'rpt_date':now, 'user_grp': curr_grp}

    return render(request, 'registration/account_admin.html', context)



# account_admin_update
@login_required
@allowed_users(allowed_roles=['admins','managers'])
def account_admin_update(request):
    now = datetime.now()
    form = AccountAdminUpdateForm(request.POST or None)

    user = request.POST.get('user')
    email = request.POST.get('email')
    group = request.POST.get('group')
    logo = request.POST.get('logo')

    context = {'rpt_date':now} #{'u_form': u_form,'p_form': p_form}

    return render(request, 'registration/account_admin_update.html', context)

# @login_required
# def view_profile(request):
#     users = User.objects.all().select_related('profile')
#     context = {'users': users}
#     return render(request, 'registration/profile.html', context)

# profile
@login_required
@allowed_users(allowed_roles=['admins','managers'])
def admin_tasks(request):
    now = datetime.now()
    #1) List all user profiles
    all_user_info = {group.name: group.user_set.values_list('username', flat=True) for group in Group.objects.all()}
    #2) Add Edit button to edit selected user

    group_user_dict = {group.name: group.user_set.values_list('id', flat=True) for group in Group.objects.all()}

    user_profile = User.objects.all().select_related('profile').exclude(groups__name='admins').order_by('-date_joined')

    #us = user_profile.filter(groups__name__in=['admins', 'brokers', 'customers', 'staffs', 'managers'])

    grp =None
    if request.user.groups.all():
        grp = request.user.groups.all()[0].name

    context = {'user_grp': grp, 'all_user_info':all_user_info, 'user_profile':user_profile, 'rpt_date':now}
    return render(request, 'registration/admin_tasks.html', context)


# admin_tasks
@login_required
@allowed_users(allowed_roles=['admins','managers'])
def admin_tasks_edit(request, req_type, pk):
    now = datetime.now()
    user = User.objects.get(pk=pk)
    curr_grp = None
    if request.user.groups.all():
        curr_grp = request.user.groups.all()[0].name

    if req_type =='del_user':
        user_id = User.objects.get(username=user).pk
        curr_grp_id = User.objects.values_list('groups__id', flat='True').get(pk=pk)
        grp_to_update = Group.objects.get(pk=curr_grp_id)
        grp_to_add = Group.objects.get(name='deactivated').id

        user.groups.remove(grp_to_update)
        user.groups.add(grp_to_add)

        messages.success(request, f'{user} account profile has successfully deactivated')
        return redirect('admin_tasks')  # Redirect back to profile page
    elif req_type =='del_logo':
        pk_user= User.objects.get(pk=pk)
        pk_user.profile.logo = 'default.jpg'
        pk_user.save()

        messages.success(request, f'{user} account profile logo has been successfully removed')
        return redirect('admin_tasks')  # Redirect back to profile page

        #old_logo= pk_user.profile.logo
    else:
        if request.method == 'POST':
            curr_grp_id = User.objects.values_list('groups__id', flat='True').filter(username=user).first()
            selected_grp_name=request.POST.get('name')
            if selected_grp_name=="":
                 selected_grp_name="deactivated"

            selected_grp_id = Group.objects.get(name=selected_grp_name).id

            u_form = UserUpdateForm(request.POST or None, files=request.FILES, instance=user) #adminTaskProfileUpdateForm(request.POST or None, files=request.FILES, instance=user)
            g_form = GroupUpdateForm(request.POST, request.FILES, instance=user)
            p_form = ProfileUpdateForm(request.POST,request.FILES,instance=user.profile)

            if u_form.is_valid() and g_form.is_valid() and p_form.is_valid():
                grp_to_update = Group.objects.get(pk=curr_grp_id)
                grp_to_add = Group.objects.get(pk=selected_grp_id)

                user.groups.remove(grp_to_update)
                user.groups.add(grp_to_add)

                u_form.save()
                g_form.save()
                p_form.save()

                messages.success(request, f'{user} account profile has successfully updated')
                return redirect('admin_tasks')  # Redirect back to profile page
            else:
                messages.error(request, f"Please fill in all required fields before proceeding {u_form.errors.as_data()}")
        else:
            email = user.email

            grp = User.objects.values_list('groups__name', flat='True').filter(username=user).first()
            logo = user.profile.logo

            u_form = UserUpdateForm(instance=user, initial = {'username':user, 'email':email}) #adminTaskProfileUpdateForm(instance=user, initial = {'username':user, 'email':email, 'group': grp, 'logo': logo })
            g_form = GroupUpdateForm(instance=user, initial={'name': grp})
            p_form = ProfileUpdateForm(instance=user.profile, initial = {'email':email})


    context = {'u_form': u_form,'g_form': g_form, 'p_form': p_form, 'rpt_date':now, 'user_grp': curr_grp, 'profile_pk':pk}

    return render(request, 'registration/admin_tasks_edit.html', context)



# admin_tasks_add
@login_required
@allowed_users(allowed_roles=['admins','managers'])
def admin_tasks_add(request):
    now = datetime.now()
    curr_grp = None
    #print('adding')
    if request.user.groups.all():
        curr_grp = request.user.groups.all()[0].name

    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        g_form = GroupUpdateForm(request.POST)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        user = request.POST.get('username')
        email = request.POST.get('email')
        group = request.POST.get('name')
        logo = request.POST.get('logo')
        pass1 = request.POST.get('password1')
        if group=="":
            group='Deactivated'

        if u_form.is_valid() and p_form.is_valid():
            #Save user
            u_form.save()
            #Save grp
            user_id=User.objects.get(username=user).pk
            grp_to_add = Group.objects.get(name=group)
            grp_to_add.user_set.add(user_id)
            #Save profile
            p_form.save()
            #Add Passord
            up = User.objects.get(pk=user_id)
            up.set_password(pass1)
            up.save()


            messages.success(request, f'User {user} successfully added!')
            return redirect('admin_tasks')  # Redirect back to profile page

    else:
        u_form = UserRegisterForm()
        g_form = GroupUpdateForm(initial={'name': 'deactivated'})
        p_form = ProfileUpdateForm()

    context = {'u_form': u_form,'p_form': p_form, 'g_form': g_form, 'rpt_date':now, 'user_grp': curr_grp}

    return render(request, 'registration/admin_tasks_add.html', context)

from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractMonth
#admin_tasks_stats
@login_required
@allowed_users(allowed_roles=['admins','managers'])
def admin_tasks_stats(request, stats_type):
    now = datetime.now()
    curr_grp = None
    if request.user.groups.all():
        curr_grp = request.user.groups.all()[0].name

    jda_profile_chart=""
    #jda_user_login_period_count=""

    if stats_type =='login_by_group':
        jda_profile_chart = User.objects.exclude(groups__name='admins').values('groups__name').annotate(gcount=Count('groups__name')).exclude(groups__name='deactivated').order_by('groups__name')
    elif stats_type =='login_by_period':
        #jda_profile_chart = User.objects.values('last_login').annotate(gcount=Count('last_login')).exclude(groups__name='deactivated').order_by('last_login')
        #jda_profile_chart = User.objects.values('last_login').annotate(month=TruncMonth('last_login')).annotate(gcount=Count('last_login')).exclude(groups__name='deactivated').values('month', 'gcount')
        jda_profile_chart = User.objects.exclude(last_login=None).exclude(groups__name='admins').annotate(month=TruncMonth('last_login')).values('month').annotate(gcount=Count('id')).values('month', 'gcount')
    context = {'stats_type': stats_type, 'jda_profile_chart':jda_profile_chart, 'rpt_date':now, 'user_grp': curr_grp}
    return render(request, 'registration/admin_tasks_stats.html', context)



#//////////////////////////////////////////subscription_plans/////////////////////////////////////////////////
#def subscription_plans(request):
#    return render(request, 'jdasubscriptions/subscription_plan.html')
#    #return render(request, 'registration/register.html')


#//////////////////////////////////////////subscription_type_toggle/////////////////////////////////////////////////

from django.shortcuts import render
from django.http import HttpResponseBadRequest

TEMPLATE_MAP = {
    # MAIN SUBSCRIPTION TYPES
    "customer": "jdasubscriptions/subscription_plan_customer.html",
    "institutions": "jdasubscriptions/subscription_plan_institutions.html",

    # CUSTOMER – AKWABA
    "akwaba_monthly": "jdasubscriptions/subscription_partial_cust_akwaba_monthly.html",
    "akwaba_yearly": "jdasubscriptions/subscription_partial_cust_akwaba_yearly.html",

    # CUSTOMER – AKWABA PLUS
    "akwaba_plus_monthly": "jdasubscriptions/subscription_partial_cust_akwaba_plus_monthly.html",
    "akwaba_plus_yearly": "jdasubscriptions/subscription_partial_cust_akwaba_plus_yearly.html",

    # CUSTOMER – AKWABA GOLD
    "akwaba_gold_monthly": "jdasubscriptions/subscription_partial_cust_akwaba_gold_monthly.html",
    "akwaba_gold_yearly": "jdasubscriptions/subscription_partial_cust_akwaba_gold_yearly.html",

    # INSTITUTIONS – SILVER
    "inst_silver_monthly": "jdasubscriptions/subscription_partial_inst_silver_monthly.html",
    "inst_silver_quarterly": "jdasubscriptions/subscription_partial_inst_silver_quarterly.html",
    "inst_silver_yearly": "jdasubscriptions/subscription_partial_inst_silver_yearly.html",

    # INSTITUTIONS – GOLD
    "inst_gold_monthly": "jdasubscriptions/subscription_partial_inst_gold_monthly.html",
    "inst_gold_quarterly": "jdasubscriptions/subscription_partial_inst_gold_quarterly.html",
    "inst_gold_yearly": "jdasubscriptions/subscription_partial_inst_gold_yearly.html",
}


def subscription_type_toggle(request):
    sub_type = request.GET.get("subscription_type")

    if not sub_type:
        return HttpResponseBadRequest("Missing subscription_type")

    plan_template = TEMPLATE_MAP.get(sub_type)

    if not plan_template:
        return HttpResponseBadRequest("Invalid subscription_type")

    context = {"sub_type": sub_type}

    return render(request, plan_template, context)


# #//////////////////////////////////////////subscription_checkout_summary/////////////////////////////////////////////////
# def subscription_checkout_summary(request):
#     """
#     HTMX endpoint: render a small checkout summary showing plan + billing,
#     with an auth-panel target that can load login/register forms via HTMX.
#     Expects GET or POST with `plan` and `billing`.
#     """
#     plan_slug = request.GET.get('plan') or request.POST.get('plan')
#     billing = request.GET.get('billing') or request.POST.get('billing') or 'monthly'
#
#     if not plan_slug:
#         return HttpResponseBadRequest("Missing plan parameter")
#
#     # Load plan from DB, fallback to basic context if plan not found (so UI still works)
#     try:
#         plan = SubscriptionPlan.objects.get(slug=plan_slug)
#         price = plan.price_for_cycle(billing)
#     except Exception:
#         # fallback values (avoid exception during early testing)
#         plan = None
#         price = '—'
#
#     context = {
#         'plan_slug': plan_slug,
#         'plan': plan,
#         'billing': billing,
#         'price': price,
#     }
#
#     return render(request, 'jdasubscriptions/htmx/checkout_summary.html', context)
#
#
# #//////////////////////////////////////////subscription_auth_panel/////////////////////////////////////////////////
# def subscription_auth_panel(request):
#     """
#     HTMX endpoint: returns either the register form or login form fragment,
#     based on the `action` param: 'register' or 'login'.
#     """
#     action = request.GET.get('action') or request.POST.get('action') or 'register'
#     action = action.lower()
#
#     if action == 'register':
#         return render(request, 'jdasubscriptions/htmx/auth_register.html', {})
#     elif action == 'login':
#         return render(request, 'jdasubscriptions/htmx/auth_login.html', {})
#     else:
#         return HttpResponseBadRequest("Invalid action")



# #//////////////////////////////////////////subscription_type_toggle/////////////////////////////////////////////////
# def subscription_type_toggle(request):
#     #print("334")
#     sub_type = request.GET.get("subscription_type")
#     #print(sub_type)
#
#     if sub_type == 'customer':
#         plan_template ="jdasubscriptions/subscription_plan_customer.html"
#     elif sub_type == 'institutions':
#         plan_template ="jdasubscriptions/subscription_plan_institutions.html"
#     elif sub_type == 'akwaba_monthly':
#         plan_template ="jdasubscriptions/subscription_partial_cust_akwaba_monthly.html"
#     elif sub_type == 'akwaba_yearly':
#         plan_template ="jdasubscriptions/subscription_partial_cust_akwaba_yearly.html"
#     elif sub_type == 'akwaba_plus_monthly':
#         plan_template ="jdasubscriptions/subscription_partial_cust_akwaba_plus_monthly.html"
#     elif sub_type == 'akwaba_plus_yearly':
#         plan_template ="jdasubscriptions/subscription_partial_cust_akwaba_plus_yearly.html"
#     elif sub_type == 'akwaba_gold_monthly':
#         plan_template ="jdasubscriptions/subscription_partial_cust_akwaba_gold_monthly.html"
#     elif sub_type == 'akwaba_gold_yearly':
#         plan_template ="jdasubscriptions/subscription_partial_cust_akwaba_gold_yearly.html"
#     elif sub_type == 'inst_silver_monthly':
#         plan_template ="jdasubscriptions/subscription_partial_inst_silver_monthly.html"
#     elif sub_type == 'inst_silver_quarterly':
#         plan_template ="jdasubscriptions/subscription_partial_inst_silver_quarterly.html"
#     elif sub_type == 'inst_silver_yearly':
#         plan_template ="jdasubscriptions/subscription_partial_inst_silver_yearly.html"
#     elif sub_type == 'inst_gold_monthly':
#         plan_template ="jdasubscriptions/subscription_partial_inst_gold_monthly.html"
#     elif sub_type == 'inst_gold_quarterly':
#         plan_template ="jdasubscriptions/subscription_partial_inst_gold_quarterly.html"
#     elif sub_type == 'inst_gold_yearly':
#         plan_template ="jdasubscriptions/subscription_partial_inst_gold_yearly.html"
#     else:
#         pass  # complete with an exception page
#
#     context={"sub_type":sub_type}
#     return render(request, f"{plan_template}", context)




# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             auth_login(request, user)
#             return redirect('jdamainapp_home')
#         else:
#             for msg in form.error_messages:
#                 print(form.error_messages[msg])
#     else:
#         form = UserCreationForm()
#
#     context = {'form': form}
#     return render(request, 'registration/signup.html', context)
