from django.shortcuts import render, redirect
# from django.http import HttpResponse
from datetime import datetime
# from django.utils.timezone import timedelta
from . models import CompanyModel, ShareholderModel, FinancialStatementFactModel, FinancialStatementLineModel, \
    FinancialStatementBalLinkModel, FinancialStatementIncLinkModel, FinancialStatementInvAcctLinkModel
from jdaanalyticsapp.models import SecurityModel, StockModel, BondModel
from . forms import FinStmtDashForm, BalanceSheetForm, IncomeStatementForm, InvestmentAccountForm, CompanyForm, \
    FinancialStatementFactForm, SecurityForm, StockModelForm, BondModelForm
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib import messages
# from django.utils.dateparse import parse_date
from . utils import get_publication_period, jdafinancialsapp_migrate_bal_link_data, jdafinancialsapp_migrate_inc_link_data,jdafinancialsapp_migrate_inv_acct_link_data, yearsago

from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from accounts .decorators import allowed_users


def get_user_grp(request):
    grp = None
    if request.user.groups.all():
        grp = request.user.groups.all()[0].name
    return grp

#////////////////////////// jdafinancialsapp_home ///////////////////////
@login_required
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
    grp = get_user_grp(request)
    context = {'user_grp':grp,'bread_home':'font-weight-bold'}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_home.html', context)


#////////////////////////// jdafinancialsapp_stmts ///////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdafinancialsapp_stmts(request):
    dt = datetime.now()

    if request.method == "POST":
        form = FinStmtDashForm(request.POST)

        if form.is_valid():
            sector = form.cleaned_data['sector']
            company = form.cleaned_data['company']
            statement = form.cleaned_data['statement']
            date = form.cleaned_data['date']
            publication_period = get_publication_period(date)

            #print(f"51: sector:{sector} -  company: {company} - statement: {statement} - statement type: {statement.id} - date: {date} - publication_perid: {get_publication_period(date)}")

            if statement.id == 1:
                #print(f"53: Balance Sheet")
                return redirect('jdafinancialsapp_bal_entry_form', sector, company.id, statement, publication_period)
            elif statement.id == 2:
                #print(f"56: Income Statement")
                return redirect('jdafinancialsapp_inc_entry_form', sector, company.id, statement, publication_period)
            elif statement.id == 3:
                #print(f"59: Income Statement")
                return redirect('jdafinancialsapp_inv_acct_entry_form', sector, company.id, statement, publication_period)
            else:
                messages.warning(request, f"Unknow Financial statement type - {statement}")
                return redirect('jdafinancialsapp_stmts')
                #print(f"64 DK statement")

    else: # end if POST
        #print(f"67//// request is GET")
        form = FinStmtDashForm()

    #print(f"67///// taking us to fin_dash request {request}")
    grp = get_user_grp(request)
    context = {'user_grp':grp,'form': form, 'dt':dt, 'bread_stmts':'font-weight-bold'}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_stmts.html', context)

#////////////////////////////////////// jdafinancialsapp_bal_entry_form ///////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_bal_entry_form(request, sector, company_id, statement, entry_date):
    company=CompanyModel.objects.get(pk=company_id)
    entry_date = publication_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()

    lines = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')

    link_data = FinancialStatementBalLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
    #print(f"143: link_date: {link_data} link_data[0]: {link_data.first().id}")
    bal_data = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date)
    #print(f"81: {link_data.count()}")

    if request.method == "POST":
        #print(f"84 POST ")
        if link_data.count() > 0: # existing balance sheet
            item = FinancialStatementBalLinkModel.objects.get(pk=link_data.first().id)
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
                #print(f"100 bal exists")
                # In existing balance sheet del item associated with company and entry_date
                bal_data.delete()
                # then Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementBalLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_bal_link_data(lines, link_data, FinancialStatementFactModel)
            else:
                #print("107 new Balance Sheet")
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementBalLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_bal_link_data(lines, link_data, FinancialStatementFactModel)

            messages.success(request, f"{company.company} {entry_date} {statement} successfully saved ")
            return redirect('jdafinancialsapp_bal_rpt', sector, company.id, statement, entry_date)
        else:
            #pass
            messages.error(request, form.errors)
    else:
        #print(f"119 - GET")
        #1) Check if company and entry date exist in the link table
        link_data = FinancialStatementBalLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)

        if link_data.count() > 0:
            item = FinancialStatementBalLinkModel.objects.get(pk=link_data[0].id)
            form = BalanceSheetForm(instance=item)
            #show bal rpt
            return redirect('jdafinancialsapp_bal_rpt', sector, company.id, statement, entry_date)
        else:
            form = BalanceSheetForm()

    link = FinancialStatementBalLinkModel.objects.all()
    bal  = FinancialStatementFactModel.objects.all()
    title = f"{statement} as of {entry_date}"
    line_hearders_subs=['ACTIF']

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form': form, 'title': title, 'bal':bal, 'lines':lines,'link':link, 'line_hearders_subs':line_hearders_subs}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_entry_form.html', context)

#////////////////////////////////////// jdafinancialsapp_inc_entry_form ///////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_inc_entry_form(request, sector, company_id, statement, entry_date):
    company=CompanyModel.objects.get(pk=company_id)
    entry_date = publication_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()

    lines = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=2).order_by('financialstatementlinesequencemodel__sequence')

    link_data = FinancialStatementIncLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
    #print(f"143: link_date: {link_data} link_data[0]: {link_data.first().id}")
    inc_data = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date)
    #print(f"149: {link_data.count()}")

    if request.method == "POST":
        #print(f"152 POST ")
        if link_data.count() > 0: # existing balance sheet
            item = FinancialStatementIncLinkModel.objects.get(pk=link_data.first().id)
            form = IncomeStatementForm(request.POST, instance=item)
        else: # new balance sheet
            form = IncomeStatementForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            for i in lines:
                #print(f"157: {i}")
                instance.company_id = company.id
                instance.entry_date=entry_date
                instance.save()

            if inc_data.count() > 0:
                print(f"168 inc exists")
                # In existing inc stmt del item associated with company and entry_date
                inc_data.delete()
                # then Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementIncLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_inc_link_data(lines, link_data, FinancialStatementFactModel)
            else:
                #print("175 new Income Statement")
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementIncLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_inc_link_data(lines, link_data, FinancialStatementFactModel)

            messages.success(request, f"{company.company} {entry_date} {statement} successfully saved ")
            return redirect('jdafinancialsapp_inc_rpt', sector, company.id, statement, entry_date)
        #else:
            #pass
        #    messages.error(request, form.errors)
    else:
        #print(f"187 - GET")
        #1) Check if company and entry date exist in the link table
        link_data = FinancialStatementIncLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)

        if link_data.count() > 0:
            item = FinancialStatementIncLinkModel.objects.get(pk=link_data[0].id)
            form = IncomeStatementForm(instance=item)
            #show bal rpt
            #print("196: redirecting to inc_rpt")
            return redirect('jdafinancialsapp_inc_rpt', sector, company.id, statement, entry_date)
        else:
            form = IncomeStatementForm()

    link = FinancialStatementIncLinkModel.objects.all()
    inc  = FinancialStatementFactModel.objects.all()
    title = f"{statement} as of {entry_date}"
    line_hearders_subs=['ACTIF']

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form': form, 'title': title, 'inc':inc, 'lines':lines,'link':link, 'line_hearders_subs':line_hearders_subs}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_inc_entry_form.html', context)



#////////////////////////////////////// jdafinancialsapp_inv_acct_entry_form ///////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_inv_acct_entry_form(request, sector, company_id, statement, entry_date):
    company=CompanyModel.objects.get(pk=company_id)
    entry_date = publication_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()

    lines = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=3).order_by('financialstatementlinesequencemodel__sequence')

    link_data = FinancialStatementInvAcctLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
    #print(f"143: link_date: {link_data} link_data[0]: {link_data.first().id}")
    inc_data = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date)
    #print(f"149: {link_data.count()}")

    if request.method == "POST":
        #print(f"152 POST ")
        if link_data.count() > 0: # existing balance sheet
            item = FinancialStatementInvAcctLinkModel.objects.get(pk=link_data.first().id)
            form = InvestmentAccountForm(request.POST, instance=item)
        else: # new balance sheet
            form = InvestmentAccountForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            for i in lines:
                #print(f"157: {i}")
                instance.company_id = company.id
                instance.entry_date=entry_date
                instance.save()

            if inc_data.count() > 0:
                #print(f"168 bal exists")
                # In existing balance sheet del item associated with company and entry_date
                inc_data.delete()
                # then Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementInvAcctLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_inc_link_data(lines, link_data, FinancialStatementFactModel)
            else:
                #print("175 new Income Statement")
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementInvAcctLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_inv_acct_link_data(lines, link_data, FinancialStatementFactModel)

            messages.success(request, f"{company.company} {entry_date} {statement} successfully saved ")
            return redirect('jdafinancialsapp_inv_acct_rpt', sector, company.id, statement, entry_date)
        #else:
            #pass
        #    messages.error(request, form.errors)
    else:
        #print(f"187 - GET")
        #1) Check if company and entry date exist in the link table
        link_data = FinancialStatementInvAcctLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)

        if link_data.count() > 0:
            item = FinancialStatementInvAcctLinkModel.objects.get(pk=link_data[0].id)
            form = InvestmentAccountForm(instance=item)
            #show bal rpt
            #print("196: redirecting to inv_acct")
            return redirect('jdafinancialsapp_inv_acct_rpt', sector, company.id, statement, entry_date)
        else:
            form = InvestmentAccountForm()

    link = FinancialStatementInvAcctLinkModel.objects.all()
    inc  = FinancialStatementFactModel.objects.all()
    title = f"{statement} as of {entry_date}"
    line_hearders_subs=['ACTIF']

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form': form, 'title': title, 'inc':inc, 'lines':lines,'link':link, 'line_hearders_subs':line_hearders_subs}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_inv_acct_entry_form.html', context)

#////////////////////////// jdafinancialsapp_bal_rpt ///////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_bal_rpt(request, sector, company_id, statement, entry_date):
    print(f"95 jdafinancialsapp_bal_rpt: User {request.user}")
    company = CompanyModel.objects.get(pk=company_id)

    bal = FinancialStatementFactModel.objects.filter(company_id=company_id, entry_date=entry_date, financial_statement_line__financialstatementlinesequencemodel__financial_statement=1).order_by('id')
    title=f"{company} {statement} as of {entry_date}"
    now = datetime.now()
    stmt_params=[sector, company_id, statement, entry_date]

    grp = get_user_grp(request)
    context = {'user_grp':grp,'bread_home':'font-weight-bold', 'bal': bal, 'stmt_params':stmt_params, 'title':title, "rpt_date":now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_rpt.html', context)

#////////////////////////// jdafinancialsapp_inc_rpt ///////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_inc_rpt(request, sector, company_id, statement, entry_date):
    #print(f"297 jdafinancialsapp_inc_rpt")
    company = CompanyModel.objects.get(pk=company_id)
    entry_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()
    curr_yr =yearsago(0, entry_date_obj)
    prev_yr= yearsago(1, entry_date_obj)
    now = datetime.now()

    inc = FinancialStatementFactModel.objects.filter(company_id=company_id, entry_date=entry_date, financial_statement_line__financialstatementlinesequencemodel__financial_statement=2).order_by('id')
    inc_prev = FinancialStatementFactModel.objects.filter(company_id=company_id, entry_date=prev_yr, financial_statement_line__financialstatementlinesequencemodel__financial_statement=2).order_by('id')
    if inc_prev.count() == 0:
        inc_res = inc
        iterate_type='default'
    else:
        inc_res = zip(inc, inc_prev)
        iterate_type='zip'


    title=f"{company} {statement} as of {entry_date}"
    stmt_params=[sector, company_id, statement, entry_date]

    grp = get_user_grp(request)
    context = {'user_grp':grp,'bread_home':'font-weight-bold', 'inc_res': inc_res, 'iterate_type':iterate_type, 'stmt_params':stmt_params, 'title':title, 'curr_yr':curr_yr, 'prev_yr':prev_yr}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_inc_rpt.html', context)


#////////////////////////// jdafinancialsapp_inv_acct_rpt ///////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_inv_acct_rpt(request, sector, company_id, statement, entry_date):
    #print(f"307 jdafinancialsapp_inv_acct_rpt")
    company = CompanyModel.objects.get(pk=company_id)

    inv = FinancialStatementFactModel.objects.filter(company_id=company_id, entry_date=entry_date, financial_statement_line__financialstatementlinesequencemodel__financial_statement=3).order_by('id')

    title=f"{company} {statement} as of {entry_date}"
    now = datetime.now()
    stmt_params=[sector, company_id, statement, entry_date]

    grp = get_user_grp(request)
    context = {'user_grp':grp,'bread_home':'font-weight-bold', 'inv': inv, 'stmt_params':stmt_params, 'title':title, "rpt_date":now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_inv_acct_rpt.html', context)


#////////////////////////////////////// jdafinancialsapp_bal_edit_form ///////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_bal_edit_form(request, sector, company_id, statement, entry_date):
    #print(f"236: bal edit company_id: {company_id}")
    company=CompanyModel.objects.get(pk=company_id)
    entry_date = publication_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()

    lines = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')

    link_data = FinancialStatementBalLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
    bal_data = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date, financial_statement_line__financialstatementlinesequencemodel__financial_statement=1)

    if request.method == "POST":
        #print(f"161 POST")
        if link_data.count() > 0: # existing balance sheet
            item = FinancialStatementBalLinkModel.objects.get(pk=link_data.first().id)
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
                #print(f"98 bal exists")
                # In existing balance sheet del item associated with company and entry_date
                bal_data.delete()
                # then Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementBalLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_bal_link_data(lines, link_data, FinancialStatementFactModel)
            else:
                #print("105 new Balance Sheet")
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementBalLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_bal_link_data(lines, link_data, FinancialStatementFactModel)

            messages.success(request, f"{company.company} {entry_date} {statement} successfully saved ")
            return redirect('jdafinancialsapp_bal_rpt', sector, company.id, statement, entry_date)
        #else:
            #pass
        #    messages.error(request, form.errors)
    else:
        #print(f"GET")
        #1) Check if company and entry date exist in the link table
        link_data = FinancialStatementBalLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)

        if link_data.count() > 0:
            item = FinancialStatementBalLinkModel.objects.get(pk=link_data[0].id)
            form = BalanceSheetForm(instance=item)
        else:
            form = BalanceSheetForm()

    link = FinancialStatementBalLinkModel.objects.all()
    bal = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date, financial_statement_line__financialstatementlinesequencemodel__financial_statement=1)

    title = f"{statement} as of {entry_date}"

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form': form, 'title': title, 'bal':bal, 'lines':lines,'link':link}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_entry_form.html', context)

#////////////////////////////////////// jdafinancialsapp_inc_edit_form ///////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_inc_edit_form(request, sector, company_id, statement, entry_date):
    #print(f"300: bal edit company_id: {company_id}")
    company=CompanyModel.objects.get(pk=company_id)
    entry_date = publication_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()

    lines = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=2).order_by('financialstatementlinesequencemodel__sequence')

    link_data = FinancialStatementIncLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
    inc_data = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date, financial_statement_line__financialstatementlinesequencemodel__financial_statement=2)

    if request.method == "POST":
        #print(f"310 POST")
        if link_data.count() > 0: # existing balance sheet
            item = FinancialStatementIncLinkModel.objects.get(pk=link_data.first().id)
            form = IncomeStatementForm(request.POST, instance=item)
        else: # new balance sheet
            form = IncomeStatementForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            for i in lines:
                #print(f"157: {i}")
                instance.company_id = company.id
                instance.entry_date=entry_date
                instance.save()

            if inc_data.count() > 0:
                #print(f"325 bal exists")
                # In existing balance sheet del item associated with company and entry_date
                inc_data.delete()
                # then Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementIncLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                #print(f"332 calling migrate_inc_link_data")
                jdafinancialsapp_migrate_inc_link_data(lines, link_data, FinancialStatementFactModel)
            else:
                #print("335 new Balance Sheet")
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementIncLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                #print(f"339 calling migrate_inc_link_data")
                jdafinancialsapp_migrate_inc_link_data(lines, link_data, FinancialStatementFactModel)

            messages.success(request, f"{company.company} {entry_date} {statement} successfully saved ")
            return redirect('jdafinancialsapp_inc_rpt', sector, company.id, statement, entry_date)
        #else:
            #pass
        #    messages.error(request, form.errors)
    else:
        #print(f" 348 GET")
        #1) Check if company and entry date exist in the link table
        link_data = FinancialStatementIncLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
        #print("351")
        if link_data.count() > 0:
            #print("353")
            item = FinancialStatementIncLinkModel.objects.get(pk=link_data[0].id)
            #print(f"355 itme: {item}")
            form = IncomeStatementForm(instance=item)
        else:
            #print("358")
            form = IncomeStatementForm()

    link = FinancialStatementIncLinkModel.objects.all()
    inc = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date,financial_statement_line__financialstatementlinesequencemodel__financial_statement=2)

    title = f"{statement} as of {entry_date}"

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form': form, 'title': title, 'inc':inc, 'lines':lines,'link':link}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_inc_entry_form.html', context)



#////////////////////////////////////// jdafinancialsapp_inv_acct_edit_form ///////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_inv_acct_edit_form(request, sector, company_id, statement, entry_date):
    #print(f"458: bal edit company_id: {company_id}")
    company=CompanyModel.objects.get(pk=company_id)
    entry_date = publication_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()

    lines = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=3).order_by('financialstatementlinesequencemodel__sequence')

    link_data = FinancialStatementInvAcctLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
    inv_data = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date, financial_statement_line__financialstatementlinesequencemodel__financial_statement=3)

    if request.method == "POST":
        #print(f"468 POST")
        if link_data.count() > 0: # existing balance sheet
            item = FinancialStatementInvAcctLinkModel.objects.get(pk=link_data.first().id)
            form = InvestmentAccountForm(request.POST, instance=item)
        else: # new balance sheet
            form = InvestmentAccountForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            for i in lines:
                #print(f"157: {i}")
                instance.company_id = company.id
                instance.entry_date=entry_date
                instance.save()

            if inv_data.count() > 0:
                #print(f"325 bal exists")
                # In existing balance sheet del item associated with company and entry_date
                inv_data.delete()
                # then Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementInvAcctLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                #print(f"489 calling migrate_inc_link_data")
                jdafinancialsapp_migrate_inv_acct_link_data(lines, link_data, FinancialStatementFactModel)
            else:
                #print("492 new Balance Sheet")
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = FinancialStatementInvAcctLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                #print(f"496 calling migrate_inc_link_data")
                jdafinancialsapp_migrate_inv_acct_link_data(lines, link_data, FinancialStatementFactModel)

            messages.success(request, f"{company.company} {entry_date} {statement} successfully saved ")
            return redirect('jdafinancialsapp_inv_acct_rpt', sector, company.id, statement, entry_date)
        #else:
            #pass
        #    messages.error(request, form.errors)
    else:
        #print(f" 505 GET")
        #1) Check if company and entry date exist in the link table
        link_data = FinancialStatementInvAcctLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
        #print("508")
        if link_data.count() > 0:
            #print("509")
            item = FinancialStatementInvAcctLinkModel.objects.get(pk=link_data[0].id)
            #print(f"512 itme: {item}")
            form = InvestmentAccountForm(instance=item)
        else:
            #print("515")
            form = InvestmentAccountForm()

    link = FinancialStatementInvAcctLinkModel.objects.all()
    inv = FinancialStatementFactModel.objects.filter(company_id=company.id, entry_date=entry_date,financial_statement_line__financialstatementlinesequencemodel__financial_statement=3)

    title = f"{statement} as of {entry_date}"

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form': form, 'title': title, 'inv':inv, 'lines':lines,'link':link}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_inv_acct_entry_form.html', context)



# #/////////////////////// jdafinancialsapp_statement_rpt /////////////////////
# def jdafinancialsapp_statement_rpt(request, company_id, statement, entry_date):
#     now = datetime.now()
#     bal_data=""
#     #stmt=""
#     period=CompanyModel.objects.all()
#     date_object = datetime.strptime(entry_date, '%Y-%m-%d').date()
#
#     # Get stmt range based on rpt_date
#     lst_range = get_rpt_range_period(date_object, period[0].rpt_period)
#
#     #lst_range =get_rpt_range_period(entry_date, period[0].rpt_period)
#
#     if statement == 'Balance Sheet':
#         bal_data = FinancialStatementFactModel.objects.filter(company=company_id, entry_date__month__range=lst_range)
#         #bal_data=FinancialStatementFactModel.objects.all()#filter(financial_statement_line_id=1)#.order_by('financialstatementlinesequencemodel__sequence')
#         #bal_data =FinancialStatementFactModel.objects.filter(company__company='Ford', company__sector__sector='Auto',entry_date__year='2021',entry_date__month__range=[1,4])
#         #stmt='Balance Sheet'
#         #print(f"247:{bal_data[0].company}")
#         bold_list = [6, 11, 18, 21, 22, 165, 168, 170,178,182,183,189,191]
#
#     context={'bal_data':bal_data, 'company_id':company_id, 'stmt':statement, 'entry_date':entry_date, 'rpt_date': now, 'bold_list': bold_list}
#     return render(request, 'jdafinancialsapp/jdafinancialsapp_statement_rpt.html', context)



#////////////////////// jdafinancialsapp_new_company /////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_new_company(request):
    #print(f"121///////// jdafinancialsapp_new_company")
    if request.method == "POST":
        form =CompanyForm(request.POST)
        #data = request.POST.copy()
        #print(f"127: {request.POST.get('company')}")
        if form.is_valid():
            form.save()
            messages.success(request, f"{form.cleaned_data['company']} info successfully added ")
            return redirect('jdafinancialsapp_new_company')
        if len(form.errors) < 4:
            messages.error(request, form.errors)

        else:
            messages.error(request, f"Please complete all required fields before submitting")
        #else:
        #    messages.error(request, form.errors)
        #    return redirect('jdafinancialsapp_new_company')
        #messages.error(request, form.errors)
        #messages.error(request, "Please complete filling all required fields before proceeding...")
    else:
        form = CompanyForm()

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form':form, 'bread_new_company':'font-weight-bold'}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_new_company.html', context)



#//////////////////////////////////////// jdafinancialsapp_view_company_detail/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_view_company_detail(request, pk):
    #print(f"289 PK {pk}")
    now = datetime.now()
    company_detail =CompanyModel.objects.get(id=pk)
    #print(f"company_detail: {company_detail}")
    grp = get_user_grp(request)
    context = {'user_grp':grp,'company_detail':company_detail,'rpt_date': now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_view_company_detail.html', context)

#//////////////////////////////////////// jdafinancialsapp_company_listing/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_company_listing(request):
    now = datetime.now()
    company_listing =CompanyModel.objects.all()

    grp = get_user_grp(request)
    context = {'user_grp':grp,'company_listing':company_listing,'rpt_date': now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_company_listing.html', context)



#//////////////////////////////////////// jdafinancialsapp_delete_company_confirm/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_delete_company_confirm(request, pk):
    #print(f"387://////{pk}")
    #company_listing = PublicationCompanyModel.objects.get(pk=pk)
    comp = CompanyModel.objects.get(pk=pk)
    messages.warning(request, f"Deletion of company '{comp}' is permanent'?")
    grp = get_user_grp(request)
    context = {'user_grp':grp,'comp': comp, 'confirmation': f"Are you sure you want to permanently delete company '{comp}'?"}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_delete_company_confirm.html', context)


#//////////////////////////////////////// jdafinancialsapp_delete_company_yes/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_delete_company_yes(request, pk):
    #print(f"398://////{pk}")
    #company_listing = PublicationCompanyModel.objects.get(pk=pk)
    comp = CompanyModel.objects.get(pk=pk)
    comp.delete()
    messages.success(request, f"Successfully deleted company: '{comp}' ID #{pk}")
    context = {'comp': comp, 'confirmation': f"Are you sure you want to permanently delete company '{comp}'?"}
    return redirect('jdafinancialsapp_company_listing')
    #return render(request, 'jdapublicationsapp/jdapublicationsapp_delete_company_confirm.html', context)



#////////////////////////// jdafinancialsapp_bal_all_rpt ///////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_bal_all_rpt(request):
    bal_data = FinancialStatementFactModel.objects.values('company__company').annotate(Sum('value')) #.order_by('company', 'company__rpt_period', 'entry_date')

    grp = get_user_grp(request)
    context = {'user_grp':grp,'bread_all_bal':'font-weight-bold', 'bal_data': bal_data}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_bal_rpt.html', context)


#////////////////////////// FinancialStatementFactForm ///////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def financialStatementFactForm(request):
    #print(f"237//////////// Bal entry Form /////// ")

    if request.method == "POST":
        #print("240 - POST")
        form = FinancialStatementFactForm(request.POST)

        if form.is_valid():
            #bal_company = form.cleaned_data['bal_company']
            data = request.POST.copy()
            #print(f"247 form data: {data}")

            form.save()
            messages.success(request, "successfully created ")
            return render(request, 'jdafinancialsapp/FinancialStatementFactForm.html')

        else: #end if valid
            messages.error(request, form.errors)
            #print(f"155 form.errors {form.errors} ///////")
    else:
        fact =FinancialStatementFactModel.objects.all()
        form = FinancialStatementFactForm()
        #print("256 - GET")

    grp = get_user_grp(request)
    context = {'user_grp':grp,'form': form, 'fact':fact}
    return render(request, 'jdafinancialsapp/FinancialStatementFactForm.html', context)

#////////////////////////// jdafinancialsapp_add_stock_security ///////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_add_stock_security(request):
    #stock_model = StockModel.objects.all()
    if request.method == "POST":
        form = SecurityForm(request.POST)
        stock_form = StockModelForm(request.POST)
        #security_ticker = request.POST.get('ticker')
        #print(f"747: name: {request.POST.get('name')}")
        #print(f"748: Open_date: {request.POST.get('open_date')}")
        #data = request.POST.copy()
        #print(f": 748 {data}") #{request.POST.get('company')}")
        if form.is_valid() and stock_form.is_valid():
            security = form.save()
            stock = stock_form.save(commit=False)
            stock.security = security
            stock.save()

            messages.success(request, f"{form.cleaned_data['ticker']} info successfully added ")
            return redirect('jdafinancialsapp_add_stock_security')

        if len(form.errors) < 4:
            messages.error(request, f"Please complete filling all required fields before submitting: {form.errors} ")

        #messages.error(request, f"Test info remove b4 prod 768: {form.errors} ")
        messages.error(request, f"Please complete filling all required fields before submitting")
        #else:
        #    messages.error(request, form.errors)
        #    return redirect('jdafinancialsapp_add_security')
    else:
        print("756 : invalid")
        form = SecurityForm()
        stock_form = StockModelForm()

    grp = get_user_grp(request)
    context = {'user_grp': grp, 'form': form, 'stock_form': stock_form, 'header_title': 'Stock', 'bread_new_security': 'font-weight-bold'}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_add_stock_security.html', context)

#////////////////////////// jdafinancialsapp_add_bond_security ///////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdafinancialsapp_add_bond_security(request):
    if request.method == "POST":
        form = SecurityForm(request.POST)
        bond_form = BondModelForm(request.POST)

        if form.is_valid() and bond_form.is_valid():
            security = form.save()
            bond = bond_form.save(commit=False)
            bond.security = security
            bond.save()
            messages.success(request, f"{form.cleaned_data['ticker']} info successfully added ")
            return redirect('jdafinancialsapp_add_bond_security')

        if len(form.errors) < 4:
            messages.error(request, f"Please complete filling all required fields before submitting: {form.errors} ")

        messages.error(request, f"Test info remove b4 prod 768: {form.errors} ")
        messages.error(request, f"Please complete filling all required fields before submitting")
        #else:
        #    messages.error(request, form.errors)
        #    return redirect('jdafinancialsapp_add_security')
    else:
        print("803 : invalid")
        form = SecurityForm()
        bond_form = BondModelForm()

    grp = get_user_grp(request)
    context = {'user_grp': grp, 'form': form, 'bond_form': bond_form, 'header_title': 'Bond', 'bread_new_security': 'font-weight-bold'}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_add_bond_security.html', context)

# //////////////////////////////////////// jdafinancialsapp_security_listing/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_security_listing(request):
    now = datetime.now()
    security_listing = SecurityModel.objects.all()
    grp = get_user_grp(request)
    context = {'user_grp':grp,'security_listing':security_listing,'rpt_date': now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_security_listing.html', context)

# //////////////////////////////////////// jdafinancialsapp_view_security_detail/////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
def jdafinancialsapp_view_security_detail(request, pk):
    #print(f"289 PK {pk}")
    now = datetime.now()
    company_detail = SecurityModel.objects.get(id=pk)
    #print(f"company_detail: {company_detail}")
    grp = get_user_grp(request)
    context = {'user_grp':grp,'security_detail':company_detail,'rpt_date': now}
    return render(request, 'jdafinancialsapp/jdafinancialsapp_view_security_detail.html', context)

# # ///////////////////////////// MISC ///////////////////////////////////////////
# """ model formset test """
# from .models import Programmer, Language
# from . forms import LanguageForm
#
# def language_formset(request):
#     programmer = Programmer.objects.get(name='Ibou')
#
#     if request.method == "POST":
#         print("361 - POST")
#
#         print(f"363: {programmer} {programmer.id}")
#         languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)
#
#         formset = languageFormset(request.POST, queryset=Language.objects.filter(programmer_id=programmer.id))
#
#         if formset.is_valid():
#             print("368 formset is valid")
#             #data = request.POST.copy()
#             #print(f"247 form data: {data}")
#             instances=formset.save(commit=False)
#
#             for i in instances:
#                 i.programmer_id= programmer.id
#                 i.save()
#                 print(f"374: i.programmer_id: {i.programmer_id}")
#
#             messages.success(request, f"successfully added ")
#             return redirect('language_formset')
#
#         else: #end if valid
#             messages.error(request, formset.errors)
#             print(f"155 form.errors {formset.errors} ///////")
#     else:
#         language_count = Language.objects.all().count()
#         if language_count >0:
#             languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)
#         else:
#             languageFormset = modelformset_factory(Language, form=LanguageForm, extra=4)
#
#         #formset =languageFormset(queryset=Language.objects.filter(programmer__name='Ibou'))
#         formset = languageFormset(queryset=Language.objects.filter(programmer_id=programmer.id))
#
#     lang = Language.objects.all()
#     context={'formset':formset, 'bread_language_formset':'font-weight-bold', 'lang':lang}
#     return render(request, 'jdafinancialsapp/language_formset.html', context)


# """ inline model formset test """
# from .models import Programmer, Language
# from . forms import LanguageForm
# from django.forms import TextInput
#
# def language_inline_formset(request):
#     programmer = Programmer.objects.get(name='Ibou')
#     languageFormset = inlineformset_factory(Programmer, Language, fields=('name',), extra=1, widgets={'name': TextInput(attrs={'class': 'form-control-sm'})})
#
#     if request.method == "POST":
#         print("406 inline - POST")
#
#         print(f"i: {programmer} {programmer.id}")
#         #languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)
#
#         formset = languageFormset(request.POST, instance=programmer)
#
#         if formset.is_valid():
#
#
#             formset.save()
#
#             messages.success(request, f"successfully added ")
#             return redirect('language_formset')
#             #return render(request, 'jdafinancialsapp/language_formset.html')
#
#         else: #end if valid
#             messages.error(request, formset.errors)
#             print(f"155 form.errors {formset.errors} ///////")
#     else:
#         print("424 Inline GET")
#         language_count = Language.objects.all().count()
#         print(language_count)
#         if language_count >0:
#             formset = languageFormset(instance=programmer)
#         #    languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)
#         else:
#             #languageFormset = inlineformset_factory(Programmer, Language, fields=('name',), extra=4, widgets={'name': TextInput(attrs={'class': 'form-control-sm'})})
#             formset = languageFormset(instance=programmer)
#             print(f"481: {programmer}")
#
#     lang = Language.objects.all()
#
#     context={'formset':formset, 'bread_language_formset':'font-weight-bold', 'lang':lang}
#     return render(request, 'jdafinancialsapp/language_formset.html', context)
#



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


# """ inline example"""
# def inline_financial_fact_formset(request):
#     company = CompanyModel.objects.get(company='Ford')
#     FinancialStatementFactFormset = inlineformset_factory(CompanyModel, FinancialStatementFactModel,  fields=('value_brut',), extra=2, widgets={'value': TextInput(attrs={'class': 'form-control-sm','placeholder':'0.00'})})
#
#     if request.method == "POST":
#         print(f"i: {company} {company.id}")
#
#         formset = FinancialStatementFactFormset(request.POST, instance=company)
#
#         if formset.is_valid():
#             #formset.save()
#             #for form in formset:
#             #    print(form.value)
#
#             messages.success(request, f"successfully added  ")
#             return redirect('financial_fact_formset')
#             #return render(request, 'jdafinancialsapp/financial_fact_formset.html')
#
#         else: #end if valid
#             messages.error(request, formset.errors)
#
#     else:
#         print("424 Inline GET")
#
#     formset = FinancialStatementFactFormset(instance=company)
#     line_items = FinancialStatementLineModel.objects.all()
#     context = {'formset': formset, 'bread_language_formset': 'font-weight-bold', 'line_items': line_items}
#
#     #context={'formset':formset, 'bread_financial_fact_formset':'font-weight-bold'}
#     return render(request, 'jdafinancialsapp/financial_fact_formset.html', context)
#

# """ shareholder_formset test """
# #def language_formset(request):
# #    programmer = Programmer.objects.get(name='Ibou')
# def shareholder_formset(request):
#     programmer = Programmer.objects.get(name='Ibou')
#
#     if request.method == "POST":
#         print("361 - POST")
#
#         print(f"363: {programmer} {programmer.id}")
#         languageFormset = modelformset_factory(Language, form=LanguageForm, extra=0)
#
#         formset = languageFormset(request.POST, queryset=Language.objects.filter(programmer_id=programmer.id))
#
#         if formset.is_valid():
#             print("368 formset is valid")
#             # data = request.POST.copy()
#             # print(f"247 form data: {data}")
#             instances = formset.save(commit=False)
#
#             for i in instances:
#                 i.programmer_id = programmer.id
#                 i.save()
#                 print(f"374: i.programmer_id: {i.programmer_id}")
#
#             messages.success(request, f"successfully added ")
#             return redirect('language_formset')
#
#         else:  # end if valid
#             messages.error(request, formset.errors)
#             print(f"155 form.errors {formset.errors} ///////")
#     else:
#         language_count = ShareholderModel.objects.all().count()
#         if language_count > 0:
#             languageFormset = modelformset_factory(ShareholderModel, form=LanguageForm, extra=0)
#         else:
#             languageFormset = modelformset_factory(ShareholderModel, form=LanguageForm, extra=4)
#
#
#         formset = languageFormset(queryset=Language.objects.filter(programmer_id=programmer.id))
#
#     lang = Language.objects.all()
#     context = {'formset': formset, 'bread_language_formset': 'font-weight-bold', 'lang': lang}
#
#     return render(request, 'jdafinancialsapp/shareholder_formset.html', context)
#
#

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