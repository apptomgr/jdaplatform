from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
# from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group

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
            messages.success(request, f'Your account has been successfully created!')
            return redirect('jdamainapp_home')
            #messages.success(request, f'Your account has been created! You are now able to log in')
            #return redirect('login')
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


# profile
#@login_required
def profile(request):
    #user=request.username
    #u_form = UserUpdateForm(instance=request.user)
    #p_form = ProfileUpdateForm(instance=request.user.profile)
    #user_profile = User.objects.all().select_related('profile')
    context={}
    #context = {'user_profile': user_profile}
    return render(request, 'registration/profile.html', context)


# profile edit
#@login_required
def profile_edit(request):
    print("pro edit")
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account profile has been updated!')
            return redirect('profile')  # Redirect back to profile page

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form,'p_form': p_form}

    return render(request, 'registration/profile_edit.html', context)


# @login_required
# def view_profile(request):
#     users = User.objects.all().select_related('profile')
#     context = {'users': users}
#     return render(request, 'registration/profile.html', context)
