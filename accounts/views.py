from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, AccountAdminForm, AccountAdminUpdateForm, GroupUpdateForm, GroupAddForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from accounts.decorators import allowed_users
from datetime import datetime
from django.db.models import Count
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
from .models import EmailVerificationToken
#from .models import SubscriptionPlan



# update registration
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.profile.phone_number = form.cleaned_data.get('phone_number', '')
            user.profile.save()
            try:
                customer_grp = Group.objects.get(name='customers')
                customer_grp.user_set.add(user)
            except Group.DoesNotExist:
                messages.warning(
                    request,
                    'Account created but group assignment failed. '
                    'Please contact us at info@jda-ci.com'
                )
            next_value = request.GET.get('next', '')
            token = EmailVerificationToken.objects.create(user=user, next_url=next_value or None)
            verification_url = f"{settings.SITE_URL}{reverse('verify_email', args=[token.token])}"
            html_message = render_to_string('registration/verification_email.html', {
                'user': user,
                'verification_url': verification_url,
            })
            send_mail(
                subject=_('Activate your JDA Platform account'),
                message=strip_tags(html_message),
                from_email=None,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True,
            )
            request.session['pending_verification_email'] = user.email
            request.session['pending_verification_username'] = user.username
            request.session['next_after_verification'] = next_value
            return redirect('verification_sent')
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


def verification_sent(request):
    email = request.session.get('pending_verification_email', '')
    return render(request, 'registration/verification_sent.html', {'email': email})


def _resolve_verified_redirect(user, session):
    """
    Shared by verify_email, verification_status, and check_verification so
    all three agree on where a just-verified user should land.

    Prefers the EmailVerificationToken.next_url captured at registration
    time — this is what makes the redirect correct even when verification
    happens in a different browser/session than registration (the mail-
    client-opens-elsewhere case). Falls back to the session value for
    in-flight tokens created before next_url existed.

    Returns (redirect_url, has_plan) so callers can pick the right message.
    """
    token = EmailVerificationToken.objects.filter(user=user).first()
    next_url = (token.next_url if token else None) or session.pop('next_after_verification', None)
    if next_url:
        return f"{reverse('login')}?next={next_url}", True
    return reverse('jdasubscriptions:subscription_plan_list'), False


def _verified_success_message(has_plan):
    if has_plan:
        return _('Your email has been verified! Please log in to continue.')
    return _('Your email has been verified! Please choose a plan to get started.')


def verify_email(request, token):
    try:
        verification = EmailVerificationToken.objects.select_related('user').get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return render(request, 'registration/verification_failed.html')

    if verification.is_expired():
        verification.delete()
        return render(request, 'registration/verification_failed.html')

    user = verification.user
    user.is_active = True
    user.save()
    # Not deleting the token here (on purpose): the original registration
    # tab may still be polling verification_status and needs to read
    # next_url after this request completes, possibly in a different
    # session. resend_verification already deletes stale tokens before
    # issuing a new one, so this doesn't collide with the OneToOneField.
    redirect_url, has_plan = _resolve_verified_redirect(user, request.session)
    messages.success(request, _verified_success_message(has_plan))
    return redirect(redirect_url)


def verification_status(request):
    """
    Polled by verification_sent.html from the original registration tab.
    Session-only lookup (no username/email parameter) so this can't be used
    to probe whether arbitrary accounts exist.
    """
    username = request.session.get('pending_verification_username')
    if not username:
        return JsonResponse({'verified': False})

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'verified': False})

    if not user.is_active:
        return JsonResponse({'verified': False})

    request.session.pop('pending_verification_username', None)
    redirect_url, has_plan = _resolve_verified_redirect(user, request.session)
    messages.success(request, _verified_success_message(has_plan))
    return JsonResponse({'verified': True, 'redirect': redirect_url})


def check_verification(request):
    username = request.session.get('pending_verification_username')
    if username:
        try:
            user = User.objects.get(username=username)
            if user.is_active:
                del request.session['pending_verification_username']
                redirect_url, has_plan = _resolve_verified_redirect(user, request.session)
                messages.success(request, _verified_success_message(has_plan))
                return redirect(redirect_url)
            else:
                messages.warning(request, _('Your email has not been verified yet. Please check your inbox.'))
                return redirect('verification_sent')
        except User.DoesNotExist:
            pass
    return redirect('login')


def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        inactive_user = User.objects.filter(email=email, is_active=False).order_by('-date_joined').first()
        if inactive_user:
            EmailVerificationToken.objects.filter(user=inactive_user).delete()
            token = EmailVerificationToken.objects.create(user=inactive_user)
            verification_url = f"{settings.SITE_URL}{reverse('verify_email', args=[token.token])}"
            html_message = render_to_string('registration/verification_email.html', {
                'user': inactive_user,
                'verification_url': verification_url,
            })
            send_mail(
                subject=_('Activate your JDA Platform account'),
                message=strip_tags(html_message),
                from_email=None,
                recipient_list=[inactive_user.email],
                html_message=html_message,
                fail_silently=True,
            )
            messages.success(
                request,
                _('If an account exists with that email, a new verification link has been sent.')
            )
        elif User.objects.filter(email=email, is_active=True).exists():
            login_url = reverse('login')
            messages.info(
                request,
                mark_safe(
                    str(_('This account is already active.'))
                    + f' <a href="{login_url}">' + str(_('Please login.')) + '</a>'
                )
            )
        else:
            messages.success(
                request,
                _('If an account exists with that email, a new verification link has been sent.')
            )
        return redirect('resend_verification')
    return render(request, 'registration/resend_verification.html')


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
    print(context)
    return render(request, 'registration/admin_tasks.html', context)


# admin_tasks
@login_required
@allowed_users(allowed_roles=['admins','managers'])
def admin_tasks_edit(request, req_type, pk):
    now = datetime.now()
    user = get_object_or_404(User, pk=pk)
    curr_grp = None
    if request.user.groups.all():
        curr_grp = request.user.groups.all()[0].name

    if req_type =='del_user':
        curr_grp_id = User.objects.values_list(
            'groups__id', flat=True
        ).filter(pk=pk).first()

        if curr_grp_id is None:
            messages.warning(request, 'User has no group assigned.')
            return redirect('admin_tasks')

        try:
            grp_to_update = Group.objects.get(pk=curr_grp_id)
            grp_to_add = Group.objects.get(name='deactivated')
        except Group.DoesNotExist:
            messages.error(
                request,
                'Group not found. Please contact info@jda-ci.com'
            )
            return redirect('admin_tasks')

        user.groups.remove(grp_to_update)
        user.groups.add(grp_to_add)

        messages.success(request, f'{user} account profile has successfully deactivated')
        return redirect('admin_tasks')  # Redirect back to profile page
    elif req_type =='del_logo':
        user.profile.logo = 'default.jpg'
        user.save()

        messages.success(request, f'{user} account profile logo has been successfully removed')
        return redirect('admin_tasks')  # Redirect back to profile page

        #old_logo= pk_user.profile.logo
    else:
        if request.method == 'POST':
            curr_grp_id = User.objects.values_list('groups__id', flat='True').filter(username=user).first()
            selected_grp_name=request.POST.get('name')
            if selected_grp_name=="":
                 selected_grp_name="deactivated"

            try:
                selected_grp_id = Group.objects.get(name=selected_grp_name).id
                grp_to_update = Group.objects.get(pk=curr_grp_id)
                grp_to_add = Group.objects.get(pk=selected_grp_id)
            except Group.DoesNotExist:
                messages.error(
                    request,
                    'Group not found. Please contact info@jda-ci.com'
                )
                return redirect('admin_tasks')

            u_form = UserUpdateForm(request.POST or None, files=request.FILES, instance=user) #adminTaskProfileUpdateForm(request.POST or None, files=request.FILES, instance=user)
            g_form = GroupUpdateForm(request.POST, request.FILES, instance=user)
            p_form = ProfileUpdateForm(request.POST,request.FILES,instance=user.profile)

            if u_form.is_valid() and g_form.is_valid() and p_form.is_valid():
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
            try:
                user_obj = User.objects.get(username=user)
                grp_to_add = Group.objects.get(name=group)
            except (User.DoesNotExist, Group.DoesNotExist):
                messages.error(
                    request,
                    'User or group not found. '
                    'Please contact info@jda-ci.com'
                )
                return redirect('admin_tasks')
            grp_to_add.user_set.add(user_obj.pk)
            #Save profile
            p_form.save()
            #Add Password
            up = user_obj
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
