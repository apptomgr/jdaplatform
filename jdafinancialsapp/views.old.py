from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime
from . models import CompanyModel, ShareholderModel, BalanceSheetModel, FinancialStatementFactModel, FinancialStatementLineModel, FinancialStatementLinkModel
from . forms import FinStmtDashForm, BalanceSheetForm, CompanyForm, ShareholderForm, FinancialStatementFactForm
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.utils.dateparse import parse_date
from . utils import get_publication_period, get_rpt_range_period, jdafinancialsapp_migrate_link_data

from django.db.models import Sum


#////////////////////////// jdafinancialsapp_home ///////////////////////
def jdafinancialsapp_home(request):
    # request.session['user_id'] = '20'
    # request.session['team'] = 'Barcelona'
    #
    # print(request.session.get('user_id'))
    # print(request.session.get('team'))
    #
    # ## delete session data
    # del request.session['user_id']
    # del request.session['team']
    #
    # print(request.session.get('user_id'))
    # print(request.session.get('team'))

    context ={'bread_home':'font-weight-bold'}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_home.html', context)


#////////////////////////// jdafinancialsapp_stmts ///////////////////////
def jdafinancialsapp_stmts(request):
    dt = datetime.now()
    print(f"36 ///////// jdafinancialsapp_stmts")

    if request.method == "POST":
        print(f"39: Posting")
        form = FinStmtDashForm(request.POST)

        if form.is_valid():
            print(f"45://////// Valid")
            sector = form.cleaned_data['sector']
            company = form.cleaned_data['company']
            statement = form.cleaned_data['statement']
            date = form.cleaned_data['date']
            publication_period = get_publication_period(date)

            print(f"51: sector:{sector} -  company: {company} - statement: {statement} - statement type: {statement.id} - date: {date} - publication_perid: {get_publication_period(date)}")

            if statement.id == 1:
                print(f"53: Balance Sheet")
                return redirect('jdafinancialsapp_bal_entry_form', sector, company.id, statement, publication_period)
            else:
                messages.warning(request, f"Unknow Financial statement type - {statement}")
                return redirect('jdafinancialsapp_stmts')
                print(f"55 DK statement")
            #rpt_date = CompanyModel.objects.values_list('rpt_period', flat=True).get(company=company)

            #lst_range = get_publication_period(date)
            #print(f"61/////////////  lst_range: {publication_perid}")

        #     #///Balance Sheet
        #     if(str(statement)=='Balance Sheet'):
        #         print(f"64: statement=Balance Sheet")
        #         bal_items = FinancialStatementFactModel.objects.filter(company__company=company, company__sector__sector=sector,
        #                                                                financial_statement_line__financialstatementlinesequencemodel__financial_statement=1,
        #                                                                entry_date=publication_perid)
        #
        #
        #         print(f"69/////////: count:{bal_items.count()}  item.first(): {bal_items.first()} item.last(): {bal_items.last()} ")
        #
        #         if bal_items.count() ==0: # bal entry doesn't exist
        #             print("72 Balance sheet does not exist")
        #             print("73 Create initial data to balance sheet instance")
        #
        #             print(f"86 company_id {company.id}")
        #             print(f"88: Redirecting to jdafinancialsapp_bal_entry_formset[{company.id}, {publication_perid}]")
        #             return redirect('jdafinancialsapp_bal_entry_formset', sector, company.id, publication_perid, statement)
        #
        #
        #         else: # bal exists
        #             print("108 Balance sheet exist")
        #             bal_entry_count = len(bal_items) #FinancialStatementFactModel.objects.all().count()
        #             print(f"110 bal_entry_count >0: {bal_entry_count}")
        #             print(f"116 company_id {company.id}")
        #             print(f"118: Redirecting to jdafinancialsapp_bal_entry_formset[company, date][{company.id}, {publication_perid}]")
        #             return redirect('jdafinancialsapp_bal_entry_formset', sector, company.id, publication_perid, statement)
        #
        #     # ///Income Stmt
        #     elif (str(statement) == 'Income Statement'):
        #         print(f"114: statement=Income Statement")
        #         inc_items = FinancialStatementFactModel.objects.filter(company__company=company, company__sector__sector=sector,
        #                                                                financial_statement_line__financialstatementlinesequencemodel__financial_statement=2,
        #                                                                entry_date=publication_perid)
        #
        #
        #         print(f"69/////////: count:{inc_items.count()}  item.first(): {inc_items.first()} item.last(): {inc_items.last()} ")
        #
        #         if inc_items.count==0: # bal entry doesn't exist
        #             print("122 Income Statement does not exist")
        #             print(f"123 company_id {company.id}")
        #             print(f"124: Redirecting to jdafinancialsapp_bal_entry_formset[{company.id}, {date}]")
        #             return redirect('jdafinancialsapp_inc_entry_formset', sector, company.id, publication_perid, statement)
        #         else: # inc exists
        #             print("127 Income Statement exist")
        #             bal_entry_count = len(inc_items) #FinancialStatementFactModel.objects.all().count()
        #             print(f"129 inc_entry_count >0: {bal_entry_count}")
        #             print(f"130 company_id {company.id}")
        #             print(f"131: Redirecting to jdafinancialsapp_inc_entry_formset[company, date][{company.id}, {publication_perid}]")
        #             return redirect('jdafinancialsapp_inc_entry_formset', sector, company.id, publication_perid, statement)
        #
        #
        #
        #     else:
        #         print(f"135: ////////// Ukn statement {statement}")
        #         messages.error(request, f"Unknow statement '{statement}' ")
        #         print(f"121: unkn stmt redirecting to jdafinancialsapp_stmts")
        #         return redirect('jdafinancialsapp_stmts')
        #
        # else: # end if valid form
        #     messages.error(request, form.errors)
        #     context = {'form': form, 'dt': dt}
        #     return render(request, 'jdafinancialsapp/jdafinancialsapp_stmts.html', context)

    else: # end if POST
        print(f"130//// request is GET")
        form = FinStmtDashForm()

    print(f"135///// taking us to fin_dash request {request}")
    context = {'form': form, 'dt':dt, 'bread_stmts':'font-weight-bold'}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_stmts.html', context)


def jdafinancialsapp_bal_entry_form(request, sector, company_id, statement, entry_date):
    company=CompanyModel.objects.get(pk=company_id)
    entry_date = publication_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()
    if statement == 'Balance Sheet':
        lines = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')

    link_data = FinancialStatementLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
    #print(f"143: link_date: {link_data} link_data[0]: {link_data.first().id}")
    bal_data = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date)
    print(f"144: {link_data.count()}")

    if request.method == "POST":
        print("148 POST")
        if link_data.count() > 0: # existing balance sheet
            item = FinancialStatementLinkModel.objects.get(pk=link_data.first().id)
            form = BalanceSheetForm(request.POST, instance=item)
        else: # new balance sheet
            form = BalanceSheetForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            for i in lines:
                #print(f"157: {i}")
                instance.company_id = company.id
                instance.entry_date=entry_date
                instance.save()

            if bal_data.count() > 0:
                print(f"278 bal exists")
                # In existing balance sheet del item associated with company and entry_date
                bal_data.delete()
                # then Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_link_data(lines, link_data, FinancialStatementFactModel)
            else:
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_link_data(lines, link_data, FinancialStatementFactModel)

            messages.success(request, f"{company.company} {entry_date} {statement} successfully saved ")
            return redirect('jdafinancialsapp_bal_rpt', sector, company.id, statement, entry_date)
        else:
            #pass
            messages.error(request, form.errors)
    else:
        print("GET")
        #1) Check if company and entry date exist in the link table
        link_data = FinancialStatementLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)

        if link_data.count() > 0:
            item = FinancialStatementLinkModel.objects.get(pk=link_data[0].id)
            #form = BalanceSheetForm(instance=item)
            #show bal rpt
            return redirect('jdafinancialsapp_bal_rpt', sector, company.id, statement, entry_date)
        else:
            form = BalanceSheetForm()

    link = FinancialStatementLinkModel.objects.all()
    bal  = FinancialStatementFactModel.objects.all()
    title = f"{statement} as of {entry_date}"

    context = {'form': form, 'title': title, 'bal':bal, 'lines':lines,'link':link}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_entry_form.html', context)


#////////////////////////// jdafinancialsapp_bal_rpt ///////////////////////
def jdafinancialsapp_bal_rpt(request, sector, company_id, statement, entry_date):
    print(f"506: {company_id} - {entry_date}")

    company = CompanyModel.objects.get(pk=company_id)

    bal = FinancialStatementFactModel.objects.filter(company_id=company_id, entry_date=entry_date).order_by('id')
    title=f"{company} {statement} as of {entry_date}"
    now = datetime.now()
    stmt_params=[sector, company_id, statement, entry_date]
    context ={'bread_home':'font-weight-bold', 'bal': bal, 'stmt_params':stmt_params, 'title':title, "rpt_date":now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_rpt.html', context)



#/////////////////////// jdafinancialsapp_statement_rpt /////////////////////
def jdafinancialsapp_statement_rpt(request, company_id, statement, entry_date):
    now = datetime.now()
    bal_data=""
    #stmt=""
    period=CompanyModel.objects.all()
    date_object = datetime.strptime(entry_date, '%Y-%m-%d').date()

    # Get stmt range based on rpt_date
    lst_range = get_rpt_range_period(date_object, period[0].rpt_period)

    #lst_range =get_rpt_range_period(entry_date, period[0].rpt_period)

    if statement == 'Balance Sheet':
        bal_data = FinancialStatementFactModel.objects.filter(company=company_id, entry_date__month__range=lst_range)
        #bal_data=FinancialStatementFactModel.objects.all()#filter(financial_statement_line_id=1)#.order_by('financialstatementlinesequencemodel__sequence')
        #bal_data =FinancialStatementFactModel.objects.filter(company__company='Ford', company__sector__sector='Auto',entry_date__year='2021',entry_date__month__range=[1,4])
        #stmt='Balance Sheet'
        #print(f"247:{bal_data[0].company}")
        bold_list = [6, 11, 18, 21, 22, 165, 168, 170,178,182,183,189,191]

    context={'bal_data':bal_data, 'company_id':company_id, 'stmt':statement, 'entry_date':entry_date, 'rpt_date': now, 'bold_list': bold_list}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_statement_rpt.html', context)



#////////////////////// jdafinancialsapp_new_company /////////////////////////
def jdafinancialsapp_new_company(request):
    print(f"121///////// jdafinancialsapp_new_company")
    if request.method == "POST":
        form =CompanyForm(request.POST)
        #data = request.POST.copy()
        #print(f"127: {request.POST.get('company')}")
        if form.is_valid():
            form.save()
            messages.success(request, f"{form.cleaned_data['company']} info successfully added ")
            return redirect('jdafinancialsapp_new_company')
        else:
            messages.error(request, form.errors)
            return redirect('jdafinancialsapp_new_company')
    else:
        form = CompanyForm()


    context={'form':form, 'bread_new_company':'font-weight-bold'}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_new_company.html', context)



#//////////////////////////////////////// jdafinancialsapp_view_company_detail/////////////////////////////
#@login_required
def jdafinancialsapp_view_company_detail(request, pk):
    print(f"289 PK {pk}")
    now = datetime.now()
    company_detail =CompanyModel.objects.get(id=pk)
    print(f"company_detail: {company_detail}")
    context = {'company_detail':company_detail,'rpt_date': now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_view_company_detail.html', context)

#//////////////////////////////////////// jdafinancialsapp_company_listing/////////////////////////////
#@login_required
def jdafinancialsapp_company_listing(request):
    now = datetime.now()
    company_listing =CompanyModel.objects.all()
    context = {'company_listing':company_listing,'rpt_date': now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_company_listing.html', context)


#////////////////////////// jdafinancialsapp_bal_edit_form ///////////////////////
def jdafinancialsapp_bal_edit_form(request, company, date, bal_pk):
    print(f"167: inside bal_edit form: {company} - {date} - {bal_pk} -  {request.method}")

    dt = datetime.now()
    if request.method == "POST":
        print("171 POST")
        item = BalanceSheetModel.objects.get(pk=bal_pk)

        form = BalanceSheetForm(request.POST or None, instance=item)
        data = request.POST.copy()
        print(f"171:////item: {item} data: {data}")
        if form.is_valid():
            form.save()
            messages.success(request, f"{item} successfully edited ")
            #messages.success(request, f"{form.cleaned_data['company']} info successfully added ")
            return redirect('jdafinancialsapp_bal_edit_form', company, date, bal_pk)
        else:
            print(f"183: Invalid ")
            messages.error(request, form.errors)
            return redirect('jdafinancialsapp_bal_edit_form', company, date, bal_pk)

    else:
        item = BalanceSheetModel.objects.get(pk=bal_pk)
        form = BalanceSheetForm(instance=item)
        title =f'{company} Balance Sheet'
        labels = BalanceSheetModel.objects.get(pk=bal_pk)
        #bal_sum_1 = BalanceSheetModel.objects.all()
        print("194: GET request form edit ")


        res =BalanceSheetModel.objects.get(pk=bal_pk)
        print(res)
        print(labels.bal_summary_1)

    context = {'title': title, 'labels':labels, 'bread_home': 'font-weight-bold', 'submit_label': 'Edit Balance Sheet',
               'form': form, 'company':company, 'date':date, 'bal_pk':bal_pk}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_edit_form.html', context)




#////////////////////////// jdafinancialsapp_bal_all_rpt ///////////////////////
def jdafinancialsapp_bal_all_rpt(request):
    bal_data = FinancialStatementFactModel.objects.values('company__company').annotate(Sum('value')) #.order_by('company', 'company__rpt_period', 'entry_date')

    context ={'bread_all_bal':'font-weight-bold', 'bal_data': bal_data}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_rpt.html', context)


def res(request):
    bal_data = BalanceSheetModel.objects.all()

    context ={'bread_home':'font-weight-bold', 'bal_data': bal_data}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_rpt.html', context)



#////////////////////////// FinancialStatementFactForm ///////////////////////
def financialStatementFactForm(request):
    print(f"237//////////// Bal entry Form /////// ")

    if request.method == "POST":
        print("240 - POST")
        form = FinancialStatementFactForm(request.POST)

        if form.is_valid():
            #bal_company = form.cleaned_data['bal_company']
            data = request.POST.copy()
            print(f"247 form data: {data}")

            form.save()
            messages.success(request, "successfully created ")
            return render(request, 'jdafinancialsapp/FinancialStatementFactForm.html')

        else: #end if valid
            messages.error(request, form.errors)
            print(f"155 form.errors {form.errors} ///////")
    else:
        fact =FinancialStatementFactModel.objects.all()
        form = FinancialStatementFactForm()
        print("256 - GET")


    context = {'form': form, 'fact':fact}
    return render(request, 'jdafinancialsapp/FinancialStatementFactForm.html', context)

""" model formset test """
from .models import Programmer, Language
from . forms import LanguageForm

def language_formset(request):
    programmer = Programmer.objects.get(name='Ibou')

    if request.method == "POST":
        print("361 - POST")

        print(f"363: {programmer} {programmer.id}")
        languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)

        formset = languageFormset(request.POST, queryset=Language.objects.filter(programmer_id=programmer.id))

        if formset.is_valid():
            print("368 formset is valid")
            #data = request.POST.copy()
            #print(f"247 form data: {data}")
            instances=formset.save(commit=False)

            for i in instances:
                i.programmer_id= programmer.id
                i.save()
                print(f"374: i.programmer_id: {i.programmer_id}")

            messages.success(request, f"successfully added ")
            return redirect('language_formset')

        else: #end if valid
            messages.error(request, formset.errors)
            print(f"155 form.errors {formset.errors} ///////")
    else:
        language_count = Language.objects.all().count()
        if language_count >0:
            languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)
        else:
            languageFormset = modelformset_factory(Language, form=LanguageForm, extra=4)

        #formset =languageFormset(queryset=Language.objects.filter(programmer__name='Ibou'))
        formset = languageFormset(queryset=Language.objects.filter(programmer_id=programmer.id))

    lang = Language.objects.all()
    context={'formset':formset, 'bread_language_formset':'font-weight-bold', 'lang':lang}
    return render(request, 'jdafinancialsapp/language_formset.html', context)


""" inline model formset test """
from .models import Programmer, Language
from . forms import LanguageForm
from django.forms import TextInput

def language_inline_formset(request):
    programmer = Programmer.objects.get(name='Ibou')
    languageFormset = inlineformset_factory(Programmer, Language, fields=('name',), extra=1, widgets={'name': TextInput(attrs={'class': 'form-control-sm'})})

    if request.method == "POST":
        print("406 inline - POST")

        print(f"i: {programmer} {programmer.id}")
        #languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)

        formset = languageFormset(request.POST, instance=programmer)

        if formset.is_valid():


            formset.save()

            messages.success(request, f"successfully added ")
            return redirect('language_formset')
            #return render(request, 'jdafinancialsapp/language_formset.html')

        else: #end if valid
            messages.error(request, formset.errors)
            print(f"155 form.errors {formset.errors} ///////")
    else:
        print("424 Inline GET")
        language_count = Language.objects.all().count()
        print(language_count)
        if language_count >0:
            formset = languageFormset(instance=programmer)
        #    languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)
        else:
            #languageFormset = inlineformset_factory(Programmer, Language, fields=('name',), extra=4, widgets={'name': TextInput(attrs={'class': 'form-control-sm'})})
            formset = languageFormset(instance=programmer)
            print(f"481: {programmer}")

    lang = Language.objects.all()

    context={'formset':formset, 'bread_language_formset':'font-weight-bold', 'lang':lang}
    return render(request, 'jdafinancialsapp/language_formset.html', context)




""" FinFact"""

def financial_fact_formset(request):
    company = CompanyModel.objects.get(company='Tesla')

    if request.method == "POST":
        print("451 - POST")

        print(f"453: {company} {company.id}")
        financial_fact_formset = modelformset_factory(FinancialStatementFactModel, form=FinancialStatementFactForm, extra=0)

        formset = financial_fact_formset(request.POST, queryset=FinancialStatementFactModel.objects.filter(company_id=company.id))

        if formset.is_valid():
            print("459 formset is valid")
            #data = request.POST.copy()
            #print(f"247 form data: {data}")
            instances=formset.save(commit=False)
            line_items = FinancialStatementLineModel.objects.all()

            for i, j in zip(instances, line_items):
                i.company_id= company.id
                i.financial_statement_line_id=j.id
                i.entry_date ='2020-03-04'
                i.save()

                print(f"468: i.company_id: {i.company_id} \nfinancial_statement_line_id: {i.financial_statement_line_id} \nentry_date: {i.entry_date}")

            messages.success(request, f"successfully added ")
            return redirect('financial_fact_formset')

        else: #end if valid
            messages.error(request, formset.errors)
            print(f"155 form.errors {formset.errors} ///////")
    else:
        print("477 GET")
        fact_count = FinancialStatementFactModel.objects.filter(company=company.id).count()
        print(f"484: {fact_count}")
        if fact_count >0:
            financial_fact_formset = modelformset_factory(FinancialStatementFactModel, form=FinancialStatementFactForm, extra=0)
        else:
            financial_fact_formset = modelformset_factory(FinancialStatementFactModel, form=FinancialStatementFactForm, extra=5)

        formset = financial_fact_formset(queryset=FinancialStatementFactModel.objects.filter(company_id=company.id))

    line_items = FinancialStatementLineModel.objects.all()
    context={'formset':formset, 'bread_language_formset':'font-weight-bold', 'line_items':line_items}
    return render(request, 'jdafinancialsapp/financial_fact_formset.html', context)


""" inline example"""
def inline_financial_fact_formset(request):
    company = CompanyModel.objects.get(company='Ford')
    FinancialStatementFactFormset = inlineformset_factory(CompanyModel, FinancialStatementFactModel,  fields=('value_brut',), extra=2, widgets={'value': TextInput(attrs={'class': 'form-control-sm','placeholder':'0.00'})})

    if request.method == "POST":
        print(f"i: {company} {company.id}")

        formset = FinancialStatementFactFormset(request.POST, instance=company)

        if formset.is_valid():
            #formset.save()
            #for form in formset:
            #    print(form.value)

            messages.success(request, f"successfully added  ")
            return redirect('financial_fact_formset')
            #return render(request, 'jdafinancialsapp/financial_fact_formset.html')

        else: #end if valid
            messages.error(request, formset.errors)

    else:
        print("424 Inline GET")

    formset = FinancialStatementFactFormset(instance=company)
    line_items = FinancialStatementLineModel.objects.all()
    context = {'formset': formset, 'bread_language_formset': 'font-weight-bold', 'line_items': line_items}

    #context={'formset':formset, 'bread_financial_fact_formset':'font-weight-bold'}
    return render(request, 'jdafinancialsapp/financial_fact_formset.html', context)


""" shareholder_formset test """
#def language_formset(request):
#    programmer = Programmer.objects.get(name='Ibou')
def shareholder_formset(request):
    programmer = Programmer.objects.get(name='Ibou')

    if request.method == "POST":
        print("361 - POST")

        print(f"363: {programmer} {programmer.id}")
        languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)

        formset = languageFormset(request.POST, queryset=Language.objects.filter(programmer_id=programmer.id))

        if formset.is_valid():
            print("368 formset is valid")
            # data = request.POST.copy()
            # print(f"247 form data: {data}")
            instances = formset.save(commit=False)

            for i in instances:
                i.programmer_id = programmer.id
                i.save()
                print(f"374: i.programmer_id: {i.programmer_id}")

            messages.success(request, f"successfully added ")
            return redirect('language_formset')

        else:  # end if valid
            messages.error(request, formset.errors)
            print(f"155 form.errors {formset.errors} ///////")
    else:
        language_count = ShareholderModel.objects.all().count()
        if language_count > 0:
            languageFormset = modelformset_factory(ShareholderModel, form=LanguageForm, extra=0)
        else:
            languageFormset = modelformset_factory(ShareholderModel, form=LanguageForm, extra=4)


        formset = languageFormset(queryset=Language.objects.filter(programmer_id=programmer.id))

    lang = Language.objects.all()
    context = {'formset': formset, 'bread_language_formset': 'font-weight-bold', 'lang': lang}

    return render(request, 'jdafinancialsapp/shareholder_formset.html', context)



#//////////////////////////////////// res/////////////////////
def res(request):
    lst_1=['h1','h2','h3']
    lst_2=[1,2,3]
    lst_fin= zip(lst_1, lst_2)
    print(lst_fin)
    context={'lst_1':lst_1, 'lst_2':lst_2, 'lst_fin':lst_fin}
    return render(request, 'jdafinancialsapp/res.html', context)


"""

#////////////////////////// jdafinancialsapp_bal_entry_form ///////////////////////
def jdafinancialsapp_bal_entry_form(request):
    #print(f"278//////////// Bal entry Form /////// ")

    dt = datetime.now()
    if request.method == "POST":
        form = FinancialStatementFactForm(request.POST) #BalanceSheetForm(request.POST)

        if form.is_valid():
            bal_type = form.cleaned_data['bal_type']
            bal_company = form.cleaned_data['bal_company']
            bal_date = form.cleaned_data['bal_date']
            #bal_item_label_1 = form.cleaned_data['bal_item_label_1']
            #bal_item_label_2 = form.cleaned_data['bal_item_label_2']
            bal_item_amt_1 = form.cleaned_data['bal_item_amt_1']
            bal_item_amt_2 = form.cleaned_data['bal_item_amt_2']
            #print(f"136: bal_item_label_1 {bal_item_label_1}")
            # data = request.POST.copy()
            print(f"134 //bal_type: {bal_type}////bal_company: {bal_company}////bal_date: {bal_date}////bal item 1: {bal_item_amt_1}////bal item 2: {bal_item_amt_2}////")

            print(f"136 ////////////// Valid //////////")
            form.save()
            messages.success(request, f"{bal_company} balance sheet successfully created ")

            #init_data = {'bal_type':bal_type, 'bal_company': bal_company, 'bal_date': bal_date, 'bal_item_amt_1':bal_item_amt_1,'bal_item_amt_2':bal_item_amt_2}
            #form = BalanceSheetForm(initial=init_data)  # Prepopulate empty for based on user selections
            title = f'Balance Sheet - {bal_company}'
            submit_label = f'Edit Balance Sheet'
            #context = {'title': title, 'form': form, 'submit_label': submit_label, 'bread_stmts': 'font-weight-bold'}
            #return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_entry_form.html', context)
            bal_data = BalanceSheetModel.objects.filter(bal_company=bal_company, bal_date=bal_date)
            context = {'title': title, 'form': form, 'submit_label': submit_label, 'bread_stmts': 'font-weight-bold', 'bal_data': bal_data}
            return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_rpt.html', context)
            #return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_rpt.html', context)
        else: #end if valid
            messages.error(request, form.errors)
            print(f"155 form.errors {form.errors} ///////")
    else:
        form = FinancialStatementFactForm()

    title = "New Balance Sheet"
    labels = FinancialStatementLineModel.objects.all()
    submit_label = 'Create new Balance Sheet'
    context = {'title': title, 'labels': labels,'form': form, 'submit_label': submit_label, 'bread_stmts': 'font-weight-bold'}

    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_entry_form.html', context)
    #return HttpResponse('res: Return balance sheet just entered')
#////////////////////////////////// jdafinancialsapp_bal_entry_formset /////////////////////////////////
def jdafinancialsapp_bal_entry_formset(request, sector, company_id, publication_date, statement):

    f"131: company.id {company_id} company"
    company = CompanyModel.objects.get(pk=company_id)
    publication_date_obj = datetime.strptime(publication_date, '%Y-%m-%d').date()
    extra=62

    if request.method == "POST":
        print("144 - POST")

        financial_fact_formset = modelformset_factory(FinancialStatementFactModel, form=FinancialStatementFactForm, extra=extra)

        formset = financial_fact_formset(request.POST, queryset=FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=publication_date_obj))

        if formset.is_valid():
            print("151 formset is valid")
            instances = formset.save(commit=False)
            line_items =FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')

            for i, j in zip(instances, line_items):
                i.company_id = company.id
                i.financial_statement_line_id = j.id
                i.entry_date = publication_date_obj
                i.save()

            messages.success(request, f"{company} {statement} successfully saved ")
            print(f"159: Redirecting to jdafinancialsapp_bal_entry_formset[company_id{company.id}]")
            return redirect('jdafinancialsapp_bal_entry_formset', sector, company.id, publication_date, statement)

        else:  # end if valid
            messages.error(request, formset.errors)
            print(f"164 form.errors {formset.errors} ///////")
    else:
        print(f"166 GET company.id: {company.id}")
        print(f"167: publication_date - {publication_date} - publication_date_obj {type(publication_date_obj)}")
        #publication_date_obj = datetime.strptime(publication_date, '%Y-%m-%d').date()
        fact_count= FinancialStatementFactModel.objects.filter(company__company=company, company__sector__sector=sector, financial_statement_line__financialstatementlinesequencemodel__financial_statement=1, entry_date=publication_date_obj).count()

        if fact_count > 0:
            print(f"172: fact_count: {fact_count} meaning bal exists")
            extra = extra - fact_count
            financial_fact_formset = modelformset_factory(FinancialStatementFactModel, form=FinancialStatementFactForm)
            formset = financial_fact_formset(queryset=FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=publication_date_obj))

        else:
            print(f"211: count=0 fact_count: {fact_count} new bal extra: {extra}")
            line_items = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')

            for i in line_items:
                #res= FinancialStatementFactModel.objects.create(company_id= company_id, financial_statement_line_id=i.id, entry_date=publication_date_obj, value_brut=0.00)}")
                res= FinancialStatementFactModel.objects.create(company_id=company_id, financial_statement_line_id=i.id, entry_date=publication_date_obj, value_brut=99.01)
                #FinancialStatementFactModel.objects.create(company=company, financial_statement_line_id=236,entry_date='2021-06-01', value_brut=0.00)

                #print(res)

            financial_fact_formset = modelformset_factory(FinancialStatementFactModel, form=FinancialStatementFactForm, extra=extra)
            formset = financial_fact_formset(queryset=FinancialStatementFactModel.objects.none())

    line_items = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')

    line_hearders_subs =['ACTIF','Immobilisations incorporelles','Immobilisations corporelles','Immobilisations financiéres',
                         'TOTAL ACTIF IMMOBILISE','Actif circulant H.A.O.', 'Ceances et emplois assimiles', 'TOTAL ACTIF CIRCULANT','TOTAL TRESORERIE ACTIF','TOTAL GENERAL',
                         'PASSIF (avant répartition)',
                         'Stocks','Créances et emplois assimilés', 'TOTAL ACTIF CIRCULANT (II)',
                         'TRESORERIE-ACTIF','TOTAL TRESSORERIE-ACTIF (III)', 'TOTAL GENERAL (I+II+III+IV)', 'TOTAL CAPITAUX PROPRES ET RESSOURCES ASSIMILEES','TOTAL DETTES FINANCIERES ET RESSOURCES ASSIMILEES','TOTAL RESSOURCES STABLES','TOTAL PASSIF CIRCULANT', 'TOTAL TRESORERIE PASSIF'
                        ]


    line_items_formset_zip = zip(line_items, formset)
    #for l, v in line_items_formset_zip:
    #         print(f"V:{v}")

    title =f"{company} Balance Sheet as of {publication_date}"

    #context = {'formset':formset2,'line_hearders_subs':line_hearders_subs, 'sector':sector, 'company_id':company.id, 'entry_date':publication_date_obj, 'statement':statement, 'title':title}
    context = {'line_items_formset_zip': line_items_formset_zip, 'formset':formset,'bread_language_formset': 'font-weight-bold', 'line_hearders_subs':line_hearders_subs, 'line_items': line_items,'sector':sector, 'company_id':company.id, 'entry_date':publication_date, 'statement':statement, 'title':title}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_entry_formset.html', context)

"""