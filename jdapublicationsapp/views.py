from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .forms import PublicationAdminsForm, PublicationFilterForm, PublicationCompanyForm, CountryForm, EmptyForm, SimpleForm, FullSearchForm
from .models import PublicationModel, PublicationCompanyModel
from accounts.models import Profile
from datetime import datetime
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from accounts .decorators import allowed_users
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from jdamainapp.utils import fitz_pdf
import re

from django.urls import resolve
import os


@login_required
def jdapublicationsapp_home(request):
    form = PublicationAdminsForm()
    full_search_form = FullSearchForm()
    filterForm =PublicationFilterForm()
    publication_listing =PublicationModel.objects.filter(visible_flag=True).all()
    #print(f"//////////17: {publication_listing.count()}/////////")
    context = {'form':form, 'filterForm':filterForm, 'publication_listing':publication_listing, 'full_search_form': full_search_form,'search_result': publication_listing}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_home.html', context)


#/////////////////////// jdapublicationsapp_dept /////////////////////
@login_required
def jdapublicationsapp_dept(request):
    context = {}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_dept.html', context)

#/////////////////////// jdapublicationsapp_pubs /////////////////////
from django.conf import settings #or from my_project import settings


@login_required
@allowed_users(allowed_roles=['admins', 'staffs', 'brokers'])
def jdapublicationsapp_pubs(request):

    form = PublicationAdminsForm()
    #full_search_form = FullSearchForm()
    filterForm = PublicationFilterForm()
    publication_listing = PublicationModel.objects.filter(visible_flag=True).all()

    # get publication_listing filenames
    my_files = []
    for i in publication_listing:
        print(f"54: i.file_name.url: {i.file_name.url}")

        x = i.file_name.name.replace("/", "~~")
        my_files.append(x)

    grp =None

    if request.user.groups.all():
        grp = request.user.groups.all()[0].name
        print(f"48 - grp: {grp}")

    if grp == 'brokers':
        # Get current user profile info (username and logo)
        curr_user = User.objects.get(username=request.user)
        #print(f"54 - curr_user: {curr_user}")
        user_profile = Profile.objects.get(user=curr_user)
        #print(f"56 - user_profile.logo: {user_profile.logo}")
        #
        # # Check the curr user logo has been already converted
        # if os.path.exists(f"{settings.MEDIA_ROOT}/profile_logo/{curr_user}_watermark.pdf"):
        #     pass  # Delete prev watermark assoc w/ user # do nothing since the logo pdf version already exist
        #     #print(f"60: Current user logo already exists for {settings.MEDIA_ROOT}/profile_logo/{curr_user}_watermark.pdf")
        # else:
        #     #print("62: File not exist convert curr user logo")
        #     #  Convert current user logo from img to pdf and save it user_watermark
        #     img2pdf(f"{settings.MEDIA_ROOT}/{user_profile.logo}", curr_user.username)  # (f"media/profile_logo/{curr_user}_watermark.pdf")

        # get candidate publication_listing filenames to prep for watermarking
        candidate_files=[]
        #print(f"68 pubs count {publication_listing.count()}")
        # Get all candidate files including full path
        for i in publication_listing:
            #print(f"i: 70 {settings.MEDIA_ROOT}/{i.file_name}")
            if not settings.DEVELOPMENT_MODE:
                candidate_files.append(i.file_name.url)
            else:
                candidate_files.append(i.file_name)


        for j in candidate_files:
            # if candidate files' extention is .pdf
            if str(j).endswith('.pdf'):
                if os.path.exists(f"{settings.MEDIA_ROOT}/{j}_{curr_user}_watermark.pdf"):
                    print(f"97: candidate file {settings.MEDIA_ROOT}/{j}_watermark.pdf exists")
                    pass  # do nothing since watermarked pdf files already exist
                else:
                    print(f"100 {settings.MEDIA_ROOT}/{j}_watermark.pdf does not exist - Applying watermarks")
                    # Apply watermark on all candidate files if they were not previously watermarked
                    fitz_pdf(f"{settings.MEDIA_ROOT}/{j}", f"{settings.MEDIA_ROOT}/{user_profile.logo}", f"{settings.MEDIA_ROOT}/{j}_{curr_user}_watermark.pdf")

                # if not settings.DEVELOPMENT_MODE:
                #     # Prod
                #     print("98 - PROD MODE")
                #     if os.path.exists(f"{j}_{curr_user}_watermark.pdf"):
                #         print(f"91: candidate file {j}_watermark.pdf exists")
                #         pass  # do nothing since watermarked pdf files already exist
                #     else:
                #         print(f"94 {j}_watermark.pdf does not exist - Applying watermarks")
                #         # Apply watermark on all candidate files if they were not previously watermarked
                #         fitz_pdf(f"{j}", f"{user_profile.logo.url}", f"{j}_{curr_user}_watermark.pdf")
                # else:
                #     # Dev mode
                #     print("107 - DEV MODE")
                #     if os.path.exists(f"{settings.MEDIA_ROOT}/{j}_{curr_user}_watermark.pdf"):
                #         print(f"108: candidate file {settings.MEDIA_ROOT}/{j}_watermark.pdf exists")
                #         pass  # do nothing since watermarked pdf files already exist
                #     else:
                #         print(f"111 {settings.MEDIA_ROOT}/{j}_watermark.pdf does not exist - Applying watermarks")
                #         # Apply watermark on all candidate files if they were not previously watermarked
                #         fitz_pdf(f"{settings.MEDIA_ROOT}/{j}", f"{settings.MEDIA_ROOT}/{user_profile.logo}", f"{settings.MEDIA_ROOT}/{j}_{curr_user}_watermark.pdf")

                    # put_watermark(
                    #     input_pdf=f"{settings.MEDIA_ROOT}/{j}",  # the original pdf
                    #     output_pdf=f"{settings.MEDIA_ROOT}/{j}_{curr_user}_watermark.pdf",  # the modified pdf with watermark
                    #     watermark=f"{settings.MEDIA_ROOT}/profile_logo/{curr_user}_watermark.pdf" # the watermark to be provided
                    #     #logo_img=f"{settings.MEDIA_ROOT}/{user_profile.logo}"
                    # )


    models_cnt=publication_listing.filter(research_category='Models').count()
    newsletters_cnt=publication_listing.filter(research_category='Newsletters').count()
    commentaries_cnt=publication_listing.filter(research_category='Commentaries').count()
    reports_cnt=publication_listing.filter(research_category='Reports').count()
    total = publication_listing.count()
    if total >0:
        per_models=(models_cnt/total) *100
        per_newsletters = round((newsletters_cnt / total) * 100)
        per_commentaries = round((commentaries_cnt / total) * 100)
        per_reports = round((reports_cnt / total) * 100)
    else:
        per_models=0
        per_newsletters=0
        per_commentaries=0
        per_reports=0

    #print(publication_listing.filename())
    # print(f"//////////17: {publication_listing.count()}/////////")
    my_list_zip = zip(publication_listing, my_files)
    context = {'form': form, 'filterForm': filterForm, 'publication_listing': publication_listing,
               'per_models':per_models,
               'per_newsletters':per_newsletters,
               'per_commentaries':per_commentaries,
               'per_reports':per_reports,
               'my_list_zip':my_list_zip,
               'user_grp':grp
               }
    #context = {'form': form, 'filterForm': filterForm, 'publication_listing': publication_listing,'full_search_form': full_search_form, 'search_result': publication_listing}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)


#/////////////////////// jdapublicationsapp_filter /////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs', 'brokers'])
def jdapublicationsapp_filter(request):
    if request.method == 'POST':
        filterForm = PublicationFilterForm(request.POST, request.FILES)
        #uploaded_file =request.FILES['file_name']
        if filterForm.is_valid():
            #print("29////////// valid request")
            from_date = filterForm.cleaned_data['from_date']
            to_date = filterForm.cleaned_data['to_date']
            author = filterForm.cleaned_data['author']
            category = filterForm.cleaned_data['research_category']
            type = filterForm.cleaned_data['research_type']
            company = filterForm.cleaned_data['company']
            #print(f"34://// from_dt:{from_date} to_date:{to_date} Author:{author} Category:{category} Type:{type} Comapny:{company}")

            # builder querystring conditions
            if from_date==None and to_date==None and author ==None and company ==None and category=='' and type =='' and company ==None: #all None
                publication_listing = PublicationModel.objects.all()
                if publication_listing:
                     messages.success(request, f"Found {publication_listing.count()} item(s) associated with all empty filters")
                     context = {'filterForm': filterForm,'publication_listing': publication_listing}
                     return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                     messages.warning(request,f"Could not find any items associated with all empty filters")

            elif from_date!=None and to_date==None and author ==None and category=='' and type =='' and company ==None and company ==None: #from_date only
                publication_listing = PublicationModel.objects.filter(publication_date=from_date)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with date value '{filterForm.cleaned_data['from_date']}'")
                    context = {'filterForm': filterForm,'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with keyword '{from_date}'")

            elif from_date!=None and to_date!=None and author ==None and category=='' and type =='' and company ==None and company ==None: #range date[from_date, to_date]
                publication_listing = PublicationModel.objects.filter(publication_date__range=(from_date, to_date))
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with date range '{from_date}' and '{to_date}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with date range '{from_date} and {to_date}'")

            elif from_date == None and to_date == None and author != None and category == '' and type == '' and company ==None and company ==None:  # Only author
                publication_listing = PublicationModel.objects.filter(author=author)
                if publication_listing:
                    messages.success(request,f"Found {publication_listing.count()} item(s) associated with author '{author}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated author '{author}'")

            elif from_date == None and to_date == None and author == None and category !='' and type == '' and company ==None and company ==None:  # Only category
                publication_listing = PublicationModel.objects.filter(research_category=category)
                if publication_listing:
                    messages.success(request,f"Found {publication_listing.count()} item(s) associated with category '{category}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated category '{category}'")

            elif from_date == None and to_date == None and author == None and category =='' and type != '' and company ==None and company ==None:  # Only Type
                publication_listing = PublicationModel.objects.filter(research_type=type)
                if publication_listing:
                    messages.success(request,f"Found {publication_listing.count()} item(s) associated with type '{type}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated type '{type}'")

            elif from_date == None and to_date == None and author == None and category =='' and type == '' and company !=None:  # Only Company
                publication_listing = PublicationModel.objects.filter(company__company_name=company)
                if publication_listing:
                    messages.success(request,f"Found {publication_listing.count()} item(s) associated with type '{company}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated type '{company}'")

            elif from_date!=None and to_date!=None and author !=None and category=='' and type =='' and company ==None: #range date[from_date, to_date] + Author
                publication_listing = PublicationModel.objects.filter(publication_date__range=(from_date, to_date), author=author)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with date range '{from_date}' and '{to_date}' and author '{author}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with date range '{from_date} and {to_date}' and author '{author}' ")

            elif from_date!=None and to_date!=None and author==None and category !='' and type =='' and company ==None: #range date[from_date, to_date] + Category
                publication_listing = PublicationModel.objects.filter(publication_date__range=(from_date, to_date), research_category=category)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with date range '{from_date}' and '{to_date}' and category '{category}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with date range '{from_date} and {to_date}' and category '{category}' ")

            elif from_date!=None and to_date!=None and author==None and category =='' and type !='' and company ==None: #range date[from_date, to_date] + type
                publication_listing = PublicationModel.objects.filter(publication_date__range=(from_date, to_date), research_type=type)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with date range '{from_date}' and '{to_date}' and type '{type}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with date range '{from_date} and '{to_date}' and type '{type}' ")

            elif from_date==None and to_date==None and author!=None and category !='' and type =='' and company ==None: #Author + category
                publication_listing = PublicationModel.objects.filter(author=author, research_category=category)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with author '{author}' and category '{category}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with author '{author} and category '{category}' ")

            elif from_date==None and to_date==None and author!=None and category =='' and type !='' and company ==None: #Author + type
                publication_listing = PublicationModel.objects.filter(author=author, research_type=type)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with author '{author}' and type '{type}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with author '{author} and type '{type}' ")

            elif from_date==None and to_date==None and author==None and category !='' and type !='' and company ==None: #category + type
                publication_listing = PublicationModel.objects.filter(research_category=category, research_type=type)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with category '{category}' and type '{type}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with category '{category} and type '{type}' ")

            elif from_date!=None and to_date!=None and author==None and category =='' and type =='' and company !=None: #dates + company
                publication_listing = PublicationModel.objects.filter(company__company_name=company, publication_date__range=(from_date, to_date))
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with date range from '{from_date}' to '{to_date}' and company '{company}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with date range from '{from_date}' to '{to_date}' and company '{company}' ")

            elif from_date==None and to_date==None and author!=None and category =='' and type =='' and company !=None: #author + company
                publication_listing = PublicationModel.objects.filter(company__company_name=company, author=author)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with Author '{author}' and company '{company}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with Author '{author}' and company '{company}' ")
            elif from_date==None and to_date==None and author==None and category !='' and type =='' and company !=None: #category + company
                publication_listing = PublicationModel.objects.filter(company__company_name=company, research_category=category)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with category '{category}' and company '{company}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with category '{category}' and company '{company}' ")
            elif from_date==None and to_date==None and author==None and category =='' and type !='' and company !=None: #type + company
                publication_listing = PublicationModel.objects.filter(company__company_name=company, research_type=type)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with type '{type}' and company '{company}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
                else:
                    messages.warning(request,f"Could not find any items associated with category '{category}' and company '{company}' ")

            #4 items
            elif from_date!=None and to_date!=None and author!=None and category !='' and type =='' and company ==None: #range date[from_date, to_date] + author + category
                publication_listing = PublicationModel.objects.filter(publication_date__range=(from_date, to_date), author=author, research_category=category)
                if publication_listing:
                    messages.success(request, f"Found {publication_listing.count()} item(s) associated with date range '{from_date}' to '{to_date}', author '{author}' and Category '{category}'")
                    context = {'filterForm': filterForm, 'publication_listing': publication_listing}
                    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)
        else:
            pass
            #print("////////168 filter form is invalid")

    else:
        filterForm =PublicationFilterForm()
        #print(filterForm)
    context = {'filterForm': filterForm}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)


#//////////////////////////////////////// jdapublicationsapp_entry/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs'])
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

    context={'form':form, 'rpt_date': now}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_entry.html', context)

#//////////////////////////////////////// jdapublicationsapp_edit/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs'])
def jdapublicationsapp_edit(request, pk):
    now = datetime.now()
    current_url = resolve(request.path_info).url_name
    #print(f"{current_url}")
    if request.method == 'POST':
        item = PublicationModel.objects.get(pk=pk)
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


        item = PublicationModel.objects.get(pk=pk)
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
    context={'form':form, 'uploaded_file':uploaded_file, 'rpt_date': now}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_entry.html', context)



#//////////////////////////////////////// jdapublicationsapp_listing/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs', 'brokers'])
def jdapublicationsapp_listing(request):
    now = datetime.now()
    publication_listing =PublicationModel.objects.all()
    context = {'publication_listing':publication_listing,'rpt_date': now}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_listing.html', context)


#//////////////////////////////////////// jdapublicationsapp_view_watermarked_pub/////////////////////////////
@login_required
@login_required
def jdapublicationsapp_view_watermarked_pub(request, file_name):
    #reconvert file_name rpl '~~' with '/'
    wm_file = file_name.replace('~~', '/')

    #get_user_logo
    curr_user =User.objects.get(username=request.user)
    user_profile=Profile.objects.get(user=curr_user)
    #print(user_profile.logo)
    #logo_path=f"media/{user_profile.logo}"
    #print(logo_path)
    #watermark file_name
    print(f"415: - {curr_user.username}")
    fitz_pdf(
        pdf_doc=f"{settings.MEDIA_ROOT}/{wm_file}",  # the original pdf
        logo=f"{settings.MEDIA_ROOT}/{curr_user.profile.logo}",  # the watermark to be provided
        pdf_out = f"{settings.MEDIA_ROOT}/{wm_file}_watermark.pdf"  # the modified pdf with watermark
        )

    #get grp info
    #if request.user.groups.exists():
    #    grp_name = request.user.groups.all()[0].name

    #    print(f"395 - grp: {grp.name}")

    context={'param_file': file_name, 'wm_file': wm_file}
    return render(request, 'jdapublicationsapp/tes.html', context)
    #return render(request, 'jdapublicationsapp/jdapublicationsapp_pubs.html', context)


#//////////////////////////////////////// jdapublicationsapp_delete/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs'])
def jdapublicationsapp_delete(request, pk):

    if request.method == 'POST':
        pub = PublicationModel.objects.get(pk=pk)
        curr_file = str(pub.file_name)
        #print(f"447: {pub.file_name}")
        #print(f"448: ^{str(pub.file_name)}.*watermark.pdf$")
        user_file = f"{curr_file}_{request.user}_watermark.pdf"
        #print(f"450: {user_file}")
        # get all user that are in the broker group
        brokers = User.objects.filter(groups__name='brokers')
        #print(f"453: {brokers}")
        for user in brokers:
            #print(f"455: {user}")
            # Check if the file about to be deleted starts with pub.file_name and ends with watermark.pdf:
            match = re.search(f"^{curr_file}.*watermark.pdf$", f"{curr_file}_{user}_watermark.pdf")
            if match:
                # delete matched files if they exist
                if os.path.exists(f"{settings.MEDIA_ROOT}/{curr_file}_{user}_watermark.pdf"):
                    os.remove(os.path.join(settings.MEDIA_ROOT, f"{curr_file}_{user}_watermark.pdf"))
                #print(f"461: match: {settings.MEDIA_ROOT}/{curr_file}_{user}_watermark.pdf")
                #print("YES! We have a match!")


        # The delete DB entry and pdf file names in MEDIA folder
        pub.delete()


        # Delete corresponding watermark files
        messages.success(request, f"Successfully deleted publication ID {pk}")
        return redirect('jdapublicationsapp_listing')


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
def jdapublicationsapp_company_listing(request):
    now =datetime.now()

    company_listing = PublicationCompanyModel.objects.all().order_by('company_name')

    context={'company_listing':company_listing,'rpt_date': now}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_company_listing.html', context)

#////////////////////// jdapublicationsapp_new_company /////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs'])
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


    context={'form':form, 'rpt_date': now}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_new_company.html', context)



#//////////////////////////////////////// jdapublicationsapp_delete_company_confirm/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs'])
def jdapublicationsapp_delete_company_confirm(request, pk):
    print(f"387://////{pk}")
    #company_listing = PublicationCompanyModel.objects.get(pk=pk)
    comp = PublicationCompanyModel.objects.get(pk=pk)
    messages.warning(request, f"Deletion of company '{comp}' is permanent'?")
    context = {'comp': comp, 'confirmation': f"Are you sure you want to permanently delete company '{comp}'?"}
    return render(request, 'jdapublicationsapp/jdapublicationsapp_delete_company_confirm.html', context)


#//////////////////////////////////////// jdapublicationsapp_delete_company_yes/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs'])
def jdapublicationsapp_delete_company_yes(request, pk):
    print(f"398://////{pk}")
    #company_listing = PublicationCompanyModel.objects.get(pk=pk)
    comp = PublicationCompanyModel.objects.get(pk=pk)
    comp.delete()
    messages.success(request, f"Successfully deleted company: '{comp}' ID #{pk}")
    context = {'comp': comp, 'confirmation': f"Are you sure you want to permanently delete company '{comp}'?"}
    return redirect('jdapublicationsapp_company_listing')
    #return render(request, 'jdapublicationsapp/jdapublicationsapp_delete_company_confirm.html', context)


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


