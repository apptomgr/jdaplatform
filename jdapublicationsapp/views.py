from django.shortcuts import render, redirect
# from django.http import HttpResponse, Http404
from .forms import PublicationAdminsForm, PublicationFilterForm, PublicationCompanyForm, CountryForm, EmptyForm, SimpleForm, FullSearchForm
from .models import PublicationModel, PublicationCompanyModel
# from accounts.models import Profile
from datetime import datetime
from django.contrib import messages
# from django.db.models import Q
from django.contrib.auth.decorators import login_required
from accounts .decorators import allowed_users
# from django.contrib.auth.decorators import user_passes_test
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.models import User
# from jdamainapp.utils import fitz_pdf
from django.utils import translation
from django.db.models import Max, Count, Q

from django.urls import resolve, reverse
from django.http import JsonResponse
from django.utils.translation import gettext
# import os


def get_user_grp(request):
    grp = None
    if request.user.groups.all():
        grp = request.user.groups.all()[0].name
    return grp


def apply_publication_filters(queryset, cleaned_data):
    """Incrementally apply PublicationFilterForm's cleaned_data onto queryset.
    Shared by jdapublicationsapp_filter (full-page POST) and the DataTables
    AJAX endpoint so both filter identically.
    """
    active_filters = []

    from_date = cleaned_data.get('from_date')
    to_date = cleaned_data.get('to_date')
    author = cleaned_data.get('author')
    category = cleaned_data.get('research_category')
    research_type = cleaned_data.get('research_type')
    company = cleaned_data.get('company')
    pub_language = cleaned_data.get('pub_language')

    if from_date and to_date:
        queryset = queryset.filter(publication_date__range=(from_date, to_date))
        active_filters.append(f"date range '{from_date}' to '{to_date}'")
    elif from_date:
        queryset = queryset.filter(publication_date__gte=from_date)
        active_filters.append(f"date from '{from_date}'")
    elif to_date:
        queryset = queryset.filter(publication_date__lte=to_date)
        active_filters.append(f"date to '{to_date}'")

    if author:
        queryset = queryset.filter(author=author)
        active_filters.append(f"author '{author}'")

    if category:
        queryset = queryset.filter(research_category=category)
        active_filters.append(f"category '{category}'")

    if research_type:
        queryset = queryset.filter(research_type=research_type)
        active_filters.append(f"type '{research_type}'")

    if company:
        queryset = queryset.filter(company=company)
        active_filters.append(f"company '{company}'")

    if pub_language:
        queryset = queryset.filter(pub_language=pub_language)
        active_filters.append(f"language '{pub_language}'")

    return queryset, active_filters

# ////////////////////////////////jdapublicationsapp_home///////////////////////////////////////
@login_required
def jdapublicationsapp_home(request):
    form = PublicationAdminsForm()
    full_search_form = FullSearchForm()
    filterForm = PublicationFilterForm()
    publication_listing = PublicationModel.objects.filter(visible_flag=True).all()
    # print(f"//////////17: {publication_listing.count()}/////////")

    grp = get_user_grp(request)
    context = {'user_grp': grp, 'form': form, 'filterForm': filterForm, 'publication_listing': publication_listing, 'full_search_form': full_search_form, 'search_result': publication_listing}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_home.html', context)


#/////////////////////// jdapublicationsapp_dept /////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdapublicationsapp_dept(request):

    grp = get_user_grp(request)
    context = {'user_grp':grp}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_dept.html', context)

#/////////////////////// jdapublicationsapp_pubs /////////////////////
@login_required
#@allowed_users(allowed_roles=['admins','managers','staffs', 'brokers'])
def jdapublicationsapp_pubs(request):
    form = PublicationAdminsForm()
    filterForm = PublicationFilterForm()

    grp = None
    if request.user.groups.all():
        grp = request.user.groups.all()[0].name

    # Row data itself is no longer loaded here: the table is populated by the
    # DataTables server-side AJAX endpoint (jdapublicationsapp_pubs_data), one
    # page at a time. This view only needs aggregate stats, not the rows.
    category_counts = dict(
        PublicationModel.objects.values('research_category')
        .annotate(cnt=Count('id'))
        .values_list('research_category', 'cnt')
    )
    total = sum(category_counts.values())
    if total > 0:
        per_newsletters = round((category_counts.get('Newsletters', 0) / total) * 100)
        per_commentaries = round((category_counts.get('Commentaries', 0) / total) * 100)
        per_reports = round((category_counts.get('Reports', 0) / total) * 100)
    else:
        per_newsletters = per_commentaries = per_reports = 0

    stats_sess = [per_newsletters, per_commentaries, per_reports]
    request.session['pub_stats_session'] = stats_sess

    curr_lang_code = translation.get_language()
    max_pub_date = PublicationModel.objects.aggregate(Max('publication_date'))
    context = {'form': form, 'filterForm': filterForm,
               'per_newsletters': per_newsletters,
               'per_commentaries': per_commentaries,
               'per_reports': per_reports,
               'user_grp': grp,
               'curr_lang_code': curr_lang_code,
               'max_pub_date': max_pub_date,
               'stats_sess': stats_sess
               }
    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)


# Columns the DataTables "order" control can target, indexed to match the
# table's column order in jdapublicationsapp_pubs.html. Columns 6/7 (Pubs,
# Expand) are action columns marked orderable:false client-side.
PUBS_ORDERABLE_COLUMNS = [
    'publication_date',
    'author__username',
    'research_category',
    'research_type',
    'subject',
    'company__company_name',
]


@login_required
def jdapublicationsapp_pubs_data(request):
    """DataTables server-side data source for the Our Publications table.

    Applies the same sidebar filters as jdapublicationsapp_filter (via the
    shared apply_publication_filters helper), but only queries and
    serializes one page of rows per request instead of the whole table.
    """
    def _int_param(name, default):
        try:
            return int(request.GET.get(name, default))
        except (TypeError, ValueError):
            return default

    draw = _int_param('draw', 1)
    start = _int_param('start', 0)
    length = _int_param('length', 10)
    if length < 0 or length > 200:
        length = 200  # defensive cap; a page is never the whole table

    base_qs = PublicationModel.objects.select_related('author', 'company')
    filterForm = PublicationFilterForm(request.GET)
    if filterForm.is_valid():
        filtered_qs, active_filters = apply_publication_filters(base_qs, filterForm.cleaned_data)
    else:
        filtered_qs = base_qs

    # DataTables' built-in search box narrows further within whatever the
    # sidebar filters already selected -- applied as an additional AND on
    # top of apply_publication_filters, never in place of it.
    search_value = request.GET.get('search[value]', '').strip()
    if search_value:
        filtered_qs = filtered_qs.filter(
            Q(subject__icontains=search_value)
            | Q(author__username__icontains=search_value)
            | Q(company__company_name__icontains=search_value)
            | Q(research_category__icontains=search_value)
            | Q(research_type__icontains=search_value)
        )

    order_col = _int_param('order[0][column]', 0)
    order_dir = request.GET.get('order[0][dir]', 'desc')
    if 0 <= order_col < len(PUBS_ORDERABLE_COLUMNS):
        order_field = PUBS_ORDERABLE_COLUMNS[order_col]
    else:
        order_field = 'publication_date'
    if order_dir == 'desc':
        order_field = f'-{order_field}'
    filtered_qs = filtered_qs.order_by(order_field)

    records_total = PublicationModel.objects.count()
    records_filtered = filtered_qs.count()

    page = filtered_qs[start:start + length]

    data = [{
        'pk': pub.pk,
        'publication_date': pub.publication_date.strftime('%Y-%m-%d'),
        'author': str(pub.author),
        'research_category': gettext(pub.research_category),
        'research_type': gettext(pub.research_type),
        'subject': gettext(pub.subject),
        'company': str(pub.company) if pub.company_id else '',
        'publication_desc': pub.publication_desc,
        'file_name': pub.file_name.name,
        'uploaded_at': pub.uploaded_at.strftime('%Y-%m-%d %H:%M'),
        'view_url': reverse('protected_publication', args=[pub.pk]),
    } for pub in page]

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


# publications/views.py
from django.http import FileResponse, JsonResponse, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import get_object_or_404
import os

from .models import PublicationModel  # adjust import to your model

ALLOWED_GROUPS = ['admins', 'managers', 'staffs', 'brokers']

def user_in_allowed_groups(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=ALLOWED_GROUPS).exists()


#///////////////////////////////////protected_publication_by_pk////////////////////////////////////////
#from django.http import FileResponse
#from django.conf import settings
from jdasubscriptions.access import (user_has_active_subscription, user_can_access_publication,)

# publications/views.py

import os

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseForbidden, Http404
#from django.shortcuts import get_object_or_404, redirect, render

#from jdapublicationsapp.models import PublicationModel
#from jdasubscriptions.services.subscription_services import user_has_active_subscription
#from jdasubscriptions.services.access_services import user_can_access_publication
# from django.http import HttpResponse
# def protected_publication_by_pk(request, pk):
#     return HttpResponse('res')

# @login_required
# def protected_publication_by_pk(request, pk):
#     print(f"167 - Eye was clicked")
#
#     publication = get_object_or_404(PublicationModel, pk=pk)
#
#     # ---------------------------------------
#     # 🔐 Staff/Admin bypass
#     # ---------------------------------------
#     if request.user.is_staff or request.user.is_superuser:
#         return redirect(
#             'protected_publication_content',
#             pk=pk
#         )
#
#     # ---------------------------------------
#     # 1️⃣ Must be subscribed
#     # ---------------------------------------
#     if not user_has_active_subscription(request.user):
#         return redirect("jdasubscriptions:subscription_plan_list")
#
#     # ---------------------------------------
#     # 2️⃣ Must be allowed by plan
#     # ---------------------------------------
#     if not user_can_access_publication(request.user, publication):
#         upgrade_data = get_upgrade_recommendation(request.user, publication)
#
#         return render(
#             request,
#             "jdasubscriptions/subscription_upgrade.html",
#             {
#                 "publication": publication,
#                 "current_plan": upgrade_data["current_plan"],
#                 "required_plan": upgrade_data["required_plan"],
#             }
#         )
#
#     pdf_url = reverse('protected_publication_content', kwargs={'pk': pk})
#     #print("285: Rendering the pdf")
#
#     return render(
#         request,
#         'jdapublicationsapp/jdapublicationsapp_pdf_viewer.html',
#         {
#             'pdf_url': pdf_url,
#             'publication': publication,
#         }
#     )


#////////////////////////////////////////////stream_publication_pdf/////////////////////////////
from django.views.decorators.clickjacking import xframe_options_exempt

#from django.http import FileResponse
#from django.shortcuts import get_object_or_404
#from django.views.decorators.clickjacking import xframe_options_exempt

#from django.http import FileResponse, Http404
#from django.shortcuts import get_object_or_404
#from django.views.decorators.clickjacking import xframe_options_exempt
import os
from django.core.exceptions import PermissionDenied


from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def stream_publication_pdf(request, pk):
    publication = get_object_or_404(PublicationModel, pk=pk)

    if not (request.user.is_staff or request.user.is_superuser):
        if not user_has_active_subscription(request.user):
            return redirect("jdasubscriptions:subscription_plan_list")
        if not user_can_access_publication(request.user, publication):
            upgrade_data = get_upgrade_recommendation(request.user, publication)
            return render(request, "jdasubscriptions/subscription_upgrade.html", {
                "publication": publication,
                "current_plan": upgrade_data["current_plan"],
                "required_plan": upgrade_data["required_plan"],
            })

    if not publication.file_name:
        raise Http404

    return FileResponse(
        publication.file_name.open('rb'),
        content_type="application/pdf",
        as_attachment=False,
    )


#///////////////////////////////////protected_publication_by_pk////////////////////////////////////////
from jdasubscriptions.access import (
    user_has_active_subscription,
    user_can_access_publication,
    get_upgrade_recommendation,
)

from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
import mimetypes
import os


def _publication_content_type(publication):
    """
    Guess the real content type from the stored filename rather than
    assuming PDF. Publications are not restricted to PDF at upload time
    (no validator on PublicationModel.file_name), so any research_type
    can end up with a non-PDF file (e.g. an .xlsx "Opinion on all stocks").
    """
    content_type, _ = mimetypes.guess_type(publication.file_name.name)
    content_type = content_type or 'application/octet-stream'
    return content_type, content_type == 'application/pdf'


@login_required
def protected_publication_by_pk(request, pk):

    publication = get_object_or_404(PublicationModel, pk=pk)

    # ---------------------------------------
    # 🔐 Staff/Admin bypass subscription checks
    # ---------------------------------------
    if not (request.user.is_staff or request.user.is_superuser):

        # 1️⃣ Must be subscribed
        if not user_has_active_subscription(request.user):
            return redirect("jdasubscriptions:subscription_plan_list")

        # 2️⃣ Must be allowed by plan
        if not user_can_access_publication(request.user, publication):

            upgrade_data = get_upgrade_recommendation(request.user, publication)

            return render(
                request,
                "jdasubscriptions/subscription_upgrade.html",
                {
                    "publication": publication,
                    "current_plan": upgrade_data["current_plan"],
                    "required_plan": upgrade_data["required_plan"],
                }
            )

    # ---------------------------------------
    # Everyone reaches viewer (staff + customers)
    # ---------------------------------------
    pdf_url = reverse(
        'protected_publication_content',
        kwargs={'pk': pk}
    )

    _, is_pdf = _publication_content_type(publication)

    if not is_pdf:
        return render(
            request,
            'jdapublicationsapp/jdapublicationsapp_download_only.html',
            {
                'download_url': f"{pdf_url}?download=1",
                'publication': publication,
            }
        )

    return render(
        request,
        'jdapublicationsapp/jdapublicationsapp_pdf_viewer.html',
        {
            'pdf_url': pdf_url,
            'publication': publication,
        }
    )



@login_required
def protected_publication_content(request, pk):

    publication = get_object_or_404(PublicationModel, pk=pk)

    if not publication.file_name:
        return HttpResponseForbidden("File not found")

    content_type, is_pdf = _publication_content_type(publication)

    # ---------------------------------------
    # Staff/Admin full access
    # ---------------------------------------
    if request.user.is_staff or request.user.is_superuser:

        # Non-PDF files always download — there's no inline viewer for them.
        if not is_pdf or request.GET.get("download") == "1":
            return FileResponse(
                publication.file_name.open('rb'),
                as_attachment=True,
                filename=os.path.basename(publication.file_name.name),
                content_type=content_type
            )

        # Otherwise inline view (PDFs only)
        return FileResponse(
            publication.file_name.open('rb'),
            content_type=content_type
        )

    # ---------------------------------------
    # Normal subscription checks
    # ---------------------------------------
    if not user_has_active_subscription(request.user):
        return HttpResponseForbidden("No active subscription")

    if not user_can_access_publication(request.user, publication):
        return HttpResponseForbidden("Plan does not allow access")

    # Non-PDF files always download — there's no inline viewer for them.
    if not is_pdf:
        return FileResponse(
            publication.file_name.open('rb'),
            as_attachment=True,
            filename=os.path.basename(publication.file_name.name),
            content_type=content_type
        )

    response = FileResponse(
        publication.file_name.open('rb'),
        content_type=content_type
    )

    response["Content-Disposition"] = 'inline'
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "no-store, must-revalidate"
    response["X-Frame-Options"] = "SAMEORIGIN"

    return response

# # publications/views.py
#
# from django.shortcuts import get_object_or_404, redirect
# from django.http import FileResponse, HttpResponseForbidden
# import os
#
# from jdasubscriptions.services.access_services import (user_has_active_subscription, user_can_access_publication,)
#
# from django.http import FileResponse, HttpResponseForbidden
# from django.shortcuts import get_object_or_404
# import os
#
# def protected_publication_by_pk(request, pk):
#
#     # ---------------------------------------
#     # 1️⃣ Must be subscribed at all
#     # ---------------------------------------
#     if not user_has_active_subscription(request.user):
#         return redirect("jdasubscriptions:subscription_plan_list")
#
#     publication = get_object_or_404(PublicationModel, pk=pk)
#
#     # ---------------------------------------
#     # 2️⃣ Must be allowed by plan
#     # ---------------------------------------
#     if not user_can_access_publication(request.user, publication):
#         return redirect("jdasubscriptions:subscription_upgrade")
#
#     # ---------------------------------------
#     # 3️⃣ Serve file INLINE (not download)
#     # ---------------------------------------
#     file_path = publication.file_name.path
#
#     if not os.path.exists(file_path):
#         return HttpResponseForbidden("File not found")
#
#     response = FileResponse(
#         open(file_path, "rb"),
#         content_type="application/pdf"
#     )
#
#     response["Content-Disposition"] = (
#         f'inline; filename="{os.path.basename(file_path)}"'
#     )
#
#     return response

# def protected_publication_by_pk(request, pk):
#
#     # ---------------------------------------
#     # 1️⃣ Must be subscribed at all
#     # ---------------------------------------
#     if not user_has_active_subscription(request.user):
#         return redirect("jdasubscriptions:subscription_plan_list")
#
#     publication = get_object_or_404(PublicationModel, pk=pk)
#
#     # ---------------------------------------
#     # 2️⃣ Must be allowed by plan
#     # ---------------------------------------
#     if not user_can_access_publication(request.user, publication):
#         return redirect("jdasubscriptions:subscription_upgrade")
#         #return redirect("jdasubscriptions:subscription_plan_list")
#
#     # ---------------------------------------
#     # 3️⃣ Serve file
#     # ---------------------------------------
#     file_path = publication.file_name.path
#
#     if not os.path.exists(file_path):
#         return HttpResponseForbidden("File not found")
#
#     return FileResponse(open(file_path, "rb"), content_type="application/pdf")




# def protected_publication_by_pk(request, pk):
#
#     if not user_has_active_subscription(request.user):
#         return redirect("jdasubscriptions:subscription_plan_list")
#
#     publication = get_object_or_404(PublicationModel, pk=pk)
#
#     file_path = publication.file_name.path
#     if not os.path.exists(file_path):
#         return HttpResponseForbidden("File not found")
#
#     return FileResponse(open(file_path, "rb"), content_type="application/pdf")




# def protected_publication_by_pk(request, pk):
#     # Access control
#     if not user_in_allowed_groups(request.user):
#         #return JsonResponse({"authorized": False}, status=403)
#         return redirect('subscription-plans')
#
#     publication = get_object_or_404(PublicationModel, pk=pk)
#
#     file_path = publication.file_name.path  # full filesystem path
#
#     if not os.path.exists(file_path):
#         return HttpResponseForbidden("File not found")
#
#     return FileResponse(open(file_path, "rb"), content_type='application/pdf')




# #/////////////////////// jdapublicationsapp_pubs_lang /////////////////////
# @login_required
# @allowed_users(allowed_roles=['admins', 'staffs', 'brokers'])
# def jdapublicationsapp_pubs_lang(request, pub_lang):
#     form = PublicationAdminsForm()
#     filterForm = PublicationFilterForm()
#
#     if pub_lang == 'French':
#         publication_listing = PublicationModel.objects.filter(pub_language='French')
#     else:
#         publication_listing = PublicationModel.objects.filter(pub_language='English')
#
#     # get publication_listing filenames
#     my_files = []
#     for i in publication_listing:
#         #print(f"54: i.file_name.url: {i.file_name.url}")
#
#         x = i.file_name.name.replace("/", "~~")
#         my_files.append(x)
#
#     grp =None
#
#     if request.user.groups.all():
#         grp = request.user.groups.all()[0].name
#
#
#     models_cnt=publication_listing.filter(research_category='Models').count()
#     newsletters_cnt=publication_listing.filter(research_category='Newsletters').count()
#     commentaries_cnt=publication_listing.filter(research_category='Commentaries').count()
#     reports_cnt=publication_listing.filter(research_category='Reports').count()
#     total = publication_listing.count()
#     if total >0:
#         per_models=(models_cnt/total) *100
#         per_newsletters = round((newsletters_cnt / total) * 100)
#         per_commentaries = round((commentaries_cnt / total) * 100)
#         per_reports = round((reports_cnt / total) * 100)
#     else:
#         per_models=0
#         per_newsletters=0
#         per_commentaries=0
#         per_reports=0
#
#
#     # print(f"//////////17: {publication_listing.count()}/////////")
#     my_list_zip = zip(publication_listing, my_files)
#     context = {'form': form, 'filterForm': filterForm, 'publication_listing': publication_listing,
#                'per_models':per_models,
#                'per_newsletters':per_newsletters,
#                'per_commentaries':per_commentaries,
#                'per_reports':per_reports,
#                'my_list_zip':my_list_zip,
#                'user_grp':grp
#                }
#     #context = {'form': form, 'filterForm': filterForm, 'publication_listing': publication_listing,'full_search_form': full_search_form, 'search_result': publication_listing}
#     return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)


#/////////////////////// jdapublicationsapp_filter /////////////////////
@login_required
#@allowed_users(allowed_roles=['admins','managers','staffs', 'brokers'])
def jdapublicationsapp_filter(request):
    stats_sess = request.session.get('pub_stats_session') # stats_sess was set in jdapublicationsapp_pubs function
    if request.method == 'POST':
        filterForm = PublicationFilterForm(request.POST, request.FILES)
        if filterForm.is_valid():
            publication_listing, active_filters = apply_publication_filters(
                PublicationModel.objects.select_related('author', 'company'),
                filterForm.cleaned_data,
            )

            filter_desc = ', '.join(active_filters) if active_filters else "all empty filters"
            count = publication_listing.count()
            if count:
                messages.success(request, f"Found {count} item(s) associated with {filter_desc}")
            else:
                messages.warning(request, f"Could not find any items associated with {filter_desc}")

            max_pub_date = publication_listing.aggregate(Max('publication_date'))
            context = {'filterForm': filterForm, 'max_pub_date': max_pub_date, 'stats_sess': stats_sess}
            return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)

        else:
            pass
            #print("////////168 filter form is invalid")

    else:
        filterForm =PublicationFilterForm()
        #print(filterForm)

    grp = get_user_grp(request)
    context = {'user_grp':grp,'filterForm': filterForm}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)


#//////////////////////////////////////// jdapublicationsapp_entry/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdapublicationsapp_entry(request):
    now = datetime.now()
    if request.method == 'POST':
        form = PublicationAdminsForm(request.POST, request.FILES)

        if form.is_valid():
            pub = form.save(commit=False)
            #pub.edited_by = request.user
            #pub.save()
            #pub.author = request.user
            pub.author = form.cleaned_data['author']
            pub.publication_date = form.cleaned_data['publication_date']
            pub.edited_by = str(request.user)
            #print(f"///////////// pub.publication_date: {pub.publication_date}/////// edited_by: {pub.edited_by}")
            pub.save()

            author = form.cleaned_data['publication_date']
            dt = form.cleaned_data['author']
            #print(f"////////////////// 165: Author /////{author} /// dt: {dt}")
            uploaded_file = request.FILES['file_name']

            messages.success(request, f"Successfully saved file '{uploaded_file}'")
            return redirect('jdapublicationsapp_listing')
        else:
            messages.error(request, f"Please fill in all required fields before proceeding ")
            #messages.error(request, f"Please fill in all required fields before proceeding {form.errors.as_data()}") {% for key, value in form.errors.items %}

    else:
        form=PublicationAdminsForm()
        #print("200")

    grp = get_user_grp(request)
    curr_lang_code = translation.get_language()
    context = {'user_grp': grp,'form':form, 'rpt_date': now, 'curr_lang_code': curr_lang_code}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_entry.html', context)

#//////////////////////////////////////// jdapublicationsapp_edit/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdapublicationsapp_edit(request, pk):
    now = datetime.now()
    current_url = resolve(request.path_info).url_name
    #print(f"{current_url}")
    if request.method == 'POST':
        item = get_object_or_404(PublicationModel, pk=pk)
        form = PublicationAdminsForm(request.POST or None, files=request.FILES, instance=item)
        #customer_edit = update_customer_prof(request.POST, request.FILES, instance=request.user.customer_profile)
        #print(f"183:////item: {item.file_name}")

        #uploaded_file =request.FILES['file_name']
        #print(f"////373 {uploaded_file}")
        if form.is_valid():
            pub = form.save(commit=False)
            #pub.author = request.user
            pub.author = form.cleaned_data['author']
            pub.publication_date = form.cleaned_data['publication_date']
            pub.edited_by = str(request.user)
            pub.save()

            messages.success(request, f"Successfully edited publication '{item}'")
            return redirect('jdapublicationsapp_listing')
        else:
            messages.error(request, f"Please fill in all required fields before proceeding {form.errors.as_data()}")

    else:
        #attachment_id = request.GET['id']
        #attachment = Attachment.objects.get(pk=attachment_id)

        #form = AttachmentForm(instance=attachment)


        item = get_object_or_404(PublicationModel, pk=pk)
        form = PublicationAdminsForm(instance=item)
        #print('Files : {}'.format(request.FILES))
        #form = PublicationAdminsForm(request.FILES, instance=item)
        #form = PublicationAdminsForm(instance=item or None, files = request.FILES or None)
        #customer_edit = update_customer_prof(request.POST, request.FILES, instance=request.user.customer_profile)

        #print(f"247:{item.file_name}")
        #base = os.path.splitext(item.file_name)
        #print(f"254:{base}")
        file_name =str(item.file_name).split('/')
        uploaded_file=file_name[-1]

    grp = get_user_grp(request)
    curr_lang_code = translation.get_language()
    context = {'user_grp': grp,'form':form, 'uploaded_file':uploaded_file, 'rpt_date': now, 'curr_lang_code': curr_lang_code}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_entry.html', context)



#//////////////////////////////////////// jdapublicationsapp_listing/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs', 'brokers'])
def jdapublicationsapp_listing(request):
    now = datetime.now()
    publication_listing =PublicationModel.objects.all()

    grp = get_user_grp(request)
    curr_lang_code = translation.get_language()
    context = {'user_grp': grp,'publication_listing':publication_listing,'rpt_date': now, 'curr_lang_code': curr_lang_code}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_listing.html', context)


# #//////////////////////////////////////// jdapublicationsapp_view_watermarked_pub/////////////////////////////
# @login_required
# @login_required
# def jdapublicationsapp_view_watermarked_pub(request, file_name):
#     #reconvert file_name rpl '~~' with '/'
#     wm_file = file_name.replace('~~', '/')
#
#     #get_user_logo
#     curr_user =User.objects.get(username=request.user)
#     user_profile=Profile.objects.get(user=curr_user)
#     #print(user_profile.logo)
#     #logo_path=f"media/{user_profile.logo}"
#     #print(logo_path)
#     #watermark file_name
#     print(f"415: - {curr_user.username}")
#     fitz_pdf(
#         pdf_doc=f"{settings.MEDIA_ROOT}/{wm_file}",  # the original pdf
#         logo=f"{settings.MEDIA_ROOT}/{curr_user.profile.logo}",  # the watermark to be provided
#         pdf_out = f"{settings.MEDIA_ROOT}/{wm_file}_watermark.pdf"  # the modified pdf with watermark
#         )
#
#     #get grp info
#     #if request.user.groups.exists():
#     #    grp_name = request.user.groups.all()[0].name
#
#     #    print(f"395 - grp: {grp.name}")
#
#     context={'param_file': file_name, 'wm_file': wm_file}
#     return render(request, 'jdapublicationsapp/tes.html', context)
#     #return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)


#//////////////////////////////////////// jdapublicationsapp_delete/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdapublicationsapp_delete(request, pk):

    if request.method == 'POST':
        pub = get_object_or_404(PublicationModel, pk=pk)
        pub.delete()
        messages.success(request, f"Successfully deleted publication ID {pk}")
        return redirect('jdapublicationsapp_listing')



#
# def jdapublicationsapp_delete(request, pk):
#
#     if request.method == 'POST':
#         pub = PublicationModel.objects.get(pk=pk)
#         curr_file = str(pub.file_name)
#         #print(f"447: {pub.file_name}")
#         #print(f"448: ^{str(pub.file_name)}.*watermark.pdf$")
#         user_file = f"{curr_file}_{request.user}_watermark.pdf"
#         #print(f"450: {user_file}")
#         # get all user that are in the broker group
#         brokers = User.objects.filter(groups__name='brokers')
#         #print(f"453: {brokers}")
#         for user in brokers:
#             #print(f"455: {user}")
#             # Check if the file about to be deleted starts with pub.file_name and ends with watermark.pdf:
#             match = re.search(f"^{curr_file}.*watermark.pdf$", f"{curr_file}_{user}_watermark.pdf")
#             if match:
#                 # delete matched files if they exist
#                 if os.path.exists(f"{settings.MEDIA_ROOT}/{curr_file}_{user}_watermark.pdf"):
#                     os.remove(os.path.join(settings.MEDIA_ROOT, f"{curr_file}_{user}_watermark.pdf"))
#                 #print(f"461: match: {settings.MEDIA_ROOT}/{curr_file}_{user}_watermark.pdf")
#                 #print("YES! We have a match!")
#
#
#         # The delete DB entry and pdf file names in MEDIA folder
#         pub.delete()
#
#
#         # Delete corresponding watermark files
#         messages.success(request, f"Successfully deleted publication ID {pk}")
#         return redirect('jdapublicationsapp_listing')


"""jda_ajax_tester"""
def jda_ajax_tester(request):
    if request.method == "POST":
        country_form = CountryForm(request.POST)
        empty_form= EmptyForm(request.POST)

        if country_form.is_valid():
            #type = request.POST['type']
            name = country_form.cleaned_data['name']
            #print(f"104://////////{name}")
        else:
            #print("106:////// Invalid")
            pass
    else:
        country_form=CountryForm();
        empty_form=EmptyForm()

    context={'country_form': country_form, 'empty_form': empty_form}
    return render(request, 'jdapublicationsapp/jda_ajax_tester.html', context)



def jda_simple_form_tester(request):
    if request.method == "POST":
        simple_form = SimpleForm(request.POST)

        if simple_form.is_valid():
            name = simple_form.cleaned_data['name']

            #print(f"121://////////{name}")
        else:
            pass
            #print("124:////// Invalid")
    else:
        #print("126:simple_form init/////////")
        simple_form = SimpleForm();

    context = {'simple_form': simple_form}
    return render(request, 'jdapublicationsapp/jda_simple_form_tester.html', context)

#////////////////////// jdapublicationsapp_company_listing ////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdapublicationsapp_company_listing(request):
    now =datetime.now()

    company_listing = PublicationCompanyModel.objects.all().order_by('company_name')

    grp = get_user_grp(request)
    context = {'user_grp':grp,'company_listing':company_listing,'rpt_date': now}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_company_listing.html', context)

#////////////////////// jdapublicationsapp_new_company /////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdapublicationsapp_new_company(request):
    now = datetime.now()
    if request.method == "POST":
        form =PublicationCompanyForm(request.POST)
        #data = request.POST.copy()

        if form.is_valid():
            #name = form.cleaned_data['company_name']
            #print(f"104://////////{name}")
            form.save()
            messages.success(request, f"{form.cleaned_data['company_name']} info successfully added ")
            return redirect('jdapublicationsapp_new_company')
        #else:
        #    messages.error(request, form.errors)
        #    return redirect('jdapublicationsapp_new_company')
    else:
        form = PublicationCompanyForm()

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form':form, 'rpt_date': now}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_new_company.html', context)



#//////////////////////////////////////// jdapublicationsapp_delete_company_confirm/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdapublicationsapp_delete_company_confirm(request, pk):
    #print(f"387://////{pk}")
    #company_listing = PublicationCompanyModel.objects.get(pk=pk)
    comp = get_object_or_404(PublicationCompanyModel, pk=pk)
    messages.warning(request, f"Deletion of company '{comp}' is permanent'?")

    grp = get_user_grp(request)
    context = {'user_grp':grp,'comp': comp, 'confirmation': f"Are you sure you want to permanently delete company '{comp}'?"}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_delete_company_confirm.html', context)


#//////////////////////////////////////// jdapublicationsapp_delete_company_yes/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdapublicationsapp_delete_company_yes(request, pk):
    #print(f"398://////{pk}")
    #company_listing = PublicationCompanyModel.objects.get(pk=pk)
    comp = get_object_or_404(PublicationCompanyModel, pk=pk)
    comp.delete()
    messages.success(request, f"Successfully deleted company: '{comp}' ID #{pk}")
    context = {'comp': comp, 'confirmation': f"Are you sure you want to permanently delete company '{comp}'?"}
    return redirect('jdapublicationsapp_company_listing')
    #return render(request, 'jdapublicationsapp/jdapublicationsapp_delete_company_confirm.html', context)


# #////////////////////////// jdafinancialsapp_add_security ///////////////////////
# @login_required
# @allowed_users(allowed_roles=['admins','managers', 'staffs'])
# def jdafinancialsapp_add_security(request):
#     #print("785 Post security info")
#     if request.method == "POST":
#         form = SecurityForm(request.POST)
#         #print(request.POST.get('issuer'))
#         #data = request.POST.copy()
#         #print(f": 708 {data}") #{request.POST.get('company')}")
#         if form.is_valid():
#             form.save()
#             messages.success(request, f"{form.cleaned_data['ticker']} info successfully added ")
#             return redirect('jdafinancialsapp_add_security')
#
#         #if len(form.errors) < 6:
#         #    #messages.error(request, form.errors)
#         messages.error(request, "Please complete filling all required fields before submitting ")
#         #else:
#         #    messages.error(request, form.errors)
#         #    return redirect('jdafinancialsapp_add_security')
#     else:
#         print("inv")
#         form = SecurityForm()
#
#     grp = get_user_grp(request)
#     context = {'user_grp': grp, 'form': form, 'bread_new_security': 'font-weight-bold'}
#     return render(request, 'jdafinancialsapp/jdafinancialsapp_add_security.html', context)


# #//////////////////////////////////////// jdapublicationsapp_delete_company/////////////////////////////
# @login_required
# def jdapublicationsapp_delete_company(request, pk):
#     if request.is_ajax:
#         try:
#             comp = PublicationCompanyModel.objects.get(pk=pk)
#             comp.delete()
#             messages.success(request, f"Successfully deleted company: '{comp}' with id # {pk}")
#             return HttpResponse(f"Successfully deleted company: '{comp}' with id # {pk}")
#             return render(request, 'jdapublicationsapp/jdafinancialsapp_new_company.html', context)
#         except Exception as e:
#             messages.error(request, f"Error: {e}. Couldn't delete company: '{comp}' with id # {pk}")
#             return redirect(f"Error: {e}. Couldn't delete company: '{comp}' with id # {pk}")
#     else:
#         return Http404

#/////////////////////// jdapublicationsapp_fullSearch /////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdapublicationsapp_fullSearch(request):
    if request.method == 'POST':
        full_search_form = FullSearchForm(request.POST or None)
        if full_search_form.is_valid():
            from_date = full_search_form.cleaned_data['from_date']
            to_date = full_search_form.cleaned_data['to_date']
            author = full_search_form.cleaned_data['author']
            category = full_search_form.cleaned_data['category']
            type = full_search_form.cleaned_data['type']
            #print(f"78://// from_dt:{from_date} to_date:{to_date} Author:{author} Category:{category} Type:{type}")

            #builder querystring conditions
            if from_date==None and to_date==None and author ==None and category=='' and type =='': #all None
                search_result = PublicationModel.objects.all()
                if search_result:
                    messages.success(request, f"Found {search_result.count()} item(s) associated with all empty filters")
                    context = {'full_search_form': full_search_form,'search_result': search_result}
                    return render(request, 'jdapublicationsapp/jdaanalyticsapp_home.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with all empty filters")


            elif from_date!=None and to_date==None and author ==None and category=='' and type =='': #from_date only
                search_result = PublicationModel.objects.filter(publication_date=from_date)
                if search_result:
                    messages.success(request, f"Found {search_result.count()} item(s) associated with date value '{full_search_form.cleaned_data['from_date']}'")
                    context = {'full_search_form': full_search_form,'search_result': search_result}
                    return render(request, 'jdapublicationsapp/jdaanalyticsapp_home.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with keyword '{from_date}'")

            elif from_date!=None and to_date!=None and author ==None and category=='' and type =='': #range date[from_date, to_date]
                search_result = PublicationModel.objects.filter(publication_date__range=(from_date, to_date))
                if search_result:
                    messages.success(request, f"Found {search_result.count()} item(s) associated with date range {from_date} and {to_date}'")
                    context = {'full_search_form': full_search_form,'search_result': search_result}
                    return render(request, 'jdapublicationsapp/jdaanalyticsapp_home.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with date range '{from_date} and {to_date}'")

            elif from_date == None and to_date == None and author != None and category == '' and type == '':  # Only author
                search_result = PublicationModel.objects.filter(author=author)
                if search_result:
                    messages.success(request,f"Found {search_result.count()} item(s) associated with author {author}'")
                    context = {'full_search_form': full_search_form,'search_result': search_result}
                    return render(request, 'jdapublicationsapp/jdaanalyticsapp_home.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated author '{author}'")

            elif from_date == None and to_date == None and author == None and category !='' and type == '':  # Only category
                search_result = PublicationModel.objects.filter(research_category=category)
                if search_result:
                    messages.success(request,f"Found {search_result.count()} item(s) associated with category {category}'")
                    context = {'full_search_form': full_search_form,'search_result': search_result}
                    return render(request, 'jdapublicationsapp/jdaanalyticsapp_home.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated category '{category}'")

            elif from_date == None and to_date == None and author == None and category =='' and type != '':  # Only Type
                search_result = PublicationModel.objects.filter(research_type=type)
                if search_result:
                    messages.success(request,f"Found {search_result.count()} item(s) associated with type {type}'")
                    context = {'full_search_form': full_search_form,'search_result': search_result}
                    return render(request, 'jdapublicationsapp/jdaanalyticsapp_home.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated type '{type}'")


    else:
        full_search_form = FullSearchForm()

    context = {'full_search_form': full_search_form}
    return render(request, 'jdapublicationsapp/jdaanalyticsapp_home.html', context)


def tes(request):
    context ={}
    return render(request, 'jdapublicationsapp/tes.html', context)


def zez(request):
    context ={}
    return render(request, 'jdapublicationsapp/zez.html', context)


