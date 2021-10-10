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
#from .models import Profile
from django.core.exceptions import ObjectDoesNotExist



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
        old_logo= pk_user.profile.logo

        if old_logo:
            if old_logo.name != 'profile_logo/default.jpg':
                print(f'old_logo.name != default.jpg {old_logo}')
                print('old NOT default changed it')
                pk_user.profile.logo.delete(save=False)  # delete old image file
                pk_user.profile.logo = 'profile_logo/default.jpg'  # set default image
                pk_user.profile.save()
                print("Changed")
            else:
                print(f'old is default delete do nothing {old_logo}')
                pass
        else:
            pass

        return redirect('admin_tasks')
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



# # admin_tasks_add
# @login_required
# @allowed_users(allowed_roles=['admins','managers'])
# def admin_tasks_del_logo(request, pk):
#     user_profile = User.objects.get(pk=pk)
#     reset_profile = Profile.SetUserImageDefault()
#     print(reset_profile)
#     grp =None
#
#     if request.user.groups.all():
#         grp = request.user.groups.all()[0].name
#
#     context = {'user_grp': grp}
#     return render(request, 'registration/profile.html', context)



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
