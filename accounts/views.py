from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, AccountAdminForm, AccountAdminUpdateForm
from django.contrib.auth.models import User
# from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from accounts .decorators import allowed_users
from datetime import datetime

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
    #user=request.username
    #u_form = UserUpdateForm(instance=request.user)
    #p_form = ProfileUpdateForm(instance=request.user.profile)
    user_profile = User.objects.all().select_related('profile')
    #print(user_profile.group.name)
    grp =None

    if request.user.groups.all():
        grp = request.user.groups.all()[0].name
        #print(f"48 - grp: {grp}")

    context = {'user_grp': grp}
    return render(request, 'registration/profile.html', context)


# profile edit
@login_required
@allowed_users(allowed_roles=['admins'])
def profile_edit(request):
    #print("pro edit")
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            # Now assoc watermark with the updated logo

            messages.success(request, f'Your account profile has been updated!')
            return redirect('profile')  # Redirect back to profile page

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form,'p_form': p_form}

    return render(request, 'registration/profile_edit.html', context)


# Account admin
@login_required
@allowed_users(allowed_roles=['admins'])
def account_admin(request):
    now = datetime.now()
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


    context ={'form':form, 'rpt_date':now}  # {'u_form': u_form,'p_form': p_form}

    return render(request, 'registration/account_admin.html', context)



# account_admin_update
@login_required
@allowed_users(allowed_roles=['admins'])
def account_admin_update(request):
    now = datetime.now()
    form = AccountAdminUpdateForm(request.POST or None)

    user = request.POST.get('user')
    email = request.POST.get('email')
    group = request.POST.get('group')
    logo = request.POST.get('logo')

    print(f"user {user} - email: {email} - group {group} - logo {logo}")
    #
    # if request.method == 'POST':
    #     form = AccountAdminUpdateForm(request.POST or None) #, instance=request.user)
    #     if form.is_valid():
    #         print('valid')
    # if request.method == 'POST':
    #     u_form = UserUpdateForm(request.POST, instance=request.user)
    #     p_form = ProfileUpdateForm(request.POST,
    #                                request.FILES,
    #                                instance=request.user.profile)
    #     if u_form.is_valid() and p_form.is_valid():
    #         u_form.save()
    #         p_form.save()
    #         # Now assoc watermark with the updated logo
    #
    #         messages.success(request, f'Your account profile has been updated!')
    #         return redirect('account_admin')  # Redirect back to account admin page
    #     else:
    #         messages.error(request, f'{form.errors}')
    #
    # else:
    #     pass
    #     # u_form = UserUpdateForm(instance=request.user)
    #     # p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {} #{'u_form': u_form,'p_form': p_form}

    return render(request, 'registration/account_admin_update.html', context)

# @login_required
# def view_profile(request):
#     users = User.objects.all().select_related('profile')
#     context = {'users': users}
#     return render(request, 'registration/profile.html', context)
