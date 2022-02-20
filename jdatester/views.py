from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import CourseForm, TestModelForm #, SecurityFilterForm, FinStmtDashForm
from jdafinancialsapp.forms import FinancialStatementFactForm
from .models import Student, Book, Course, TestModel, Blog
from jdafinancialsapp.models import CompanyModel, FinancialStatementLineModel, FinancialStatementFactModel, FinancialStatementLineSequenceModel, FinancialStatementModel
from django.forms import modelformset_factory
from django.contrib import messages
from datetime import datetime
from .forms import AuthorForm, BalanceSheetForm, DashForm
from .models import Author, Book, jdatesterBalanceSheetModel, jdatesterCompanyModel, jdatesterLineModel, jdatesterLinkModel
from django.forms import modelformset_factory, inlineformset_factory
from django.db import IntegrityError
from jdafinancialsapp.utils import jdatester_publication_date, jdafinancialsapp_migrate_bal_link_data
from tablib import Dataset

from .resources import EmployeeResource
from .models import Employee



import xlrd

import pandas as pd

from django.utils.translation import gettext as _


def index(request):
    context_dict = {  # 2
        'hello': _('hello')  # 3
    }
    return render(request, 'index.html', context_dict)  # 4


def jdatester_home(request):
    form = CourseForm()

    context ={'form':form, 'hello': _('hello')}
    return render(request, 'jdatester/home.html', context)

#////////////////////////// jdatester_fact_form ///////////////////////
def jdatester_fact_form(request):
    print(f"19//////////// Bal entry Form /////// ")
    dt = datetime.now()
    if request.method == "POST":
        form = FinancialStatementFactForm(request.POST)
        #print(request.POST['code_1'])

        if form.is_valid():
            print(f"26 ////////////// Valid //////////")
            val_1= form.cleaned_data['val_1']
            val_2 = form.cleaned_data['val_2']
            data = request.POST.copy()
            print(f"30: form data: {data}")
            print(f"31 bal_company: {val_1} - val_1: {val_1} - val_2: {val_2} ")

            instance = form.save(commit=False)
            line_items =FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')

            #c = form.save(commit=False)
            #b.foreignkeytoA = a
            #b.save()
            #c.foreignkeytoB = b
            #c.save()

            #for i in line_items:
            instance.company_id = 1
            instance.financial_statement_line_id = 236
            instance.entry_date = '2020-01-01'

            instance.company_id = 1
            instance.financial_statement_line_id = 6
            instance.entry_date = '2020-01-01'

            instance.save()


            messages.success(request, f" balance sheet successfully created ")
            return redirect('jdatester_fact_form')
        else: #end if valid
            messages.error(request, form.errors)
            print(f"54 form.errors {form.errors} ///////")
            return redirect('jdatester_fact_form')
    else:
        print("GET")
        form = FinancialStatementFactForm()
        line_items = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')
        #for i in line_items:
        #    print(i.id)
    title = "New Balance Sheet"
    form_data=[1, '2021-01-01']
    context = {'title': title, 'line_items': line_items,'form': form}
    return render(request, 'jdatester/fact_form.html', context)





def jdatester_fact(request):
    fact = FinancialStatementFactModel.objects.all();
    line_items = FinancialStatementLineModel.objects.filter(financialstatementlinesequencemodel__financial_statement=1).order_by('financialstatementlinesequencemodel__sequence')

    FactFormset = modelformset_factory(FinancialStatementFactModel, fields=('value_brut','value_amort'), extra=5)
    company = CompanyModel.objects.get(company='Ford')
    publish_date_obj = datetime.strptime('2021-03-01', '%Y-%m-%d').date()
    print(f"20: company: {company} company_id: {company.id} publish_date_obj: {publish_date_obj}")

    if request.method == "POST":
        print("22 - POST")
        formset = FactFormset(request.POST, queryset=FinancialStatementFactModel.objects.filter(company_id=company.id))

        if formset.is_valid():
            print('VALID')
            instances = formset.save(commit=False)
            # line_items = FinancialStatementLineModel.objects.all()
            #print(line_items)
            for i, j in zip(instances, line_items):
                i.company_id=company.id
                i.financial_statement_line_id= j.id
                i.entry_date = publish_date_obj
                i.save()

            messages.success(request, f" successfully saved ")
            print(f"41: Redirecting to jdatester_fact[company_id: {company.id}]")
            return redirect('jdatester_fact')
        else:
            print('INVALID')
            messages.error(request, formset.errors)
    else:
        print('46: GET')
        formset = FactFormset(queryset=FinancialStatementFactModel.objects.filter(company_id=company.id))
        #line_items_formset_zip = zip(line_items, formset)

    context = {'fact':fact,'line_items':line_items,  'formset':formset}
    return render(request, 'jdatester/fact.html', context)


def test_model(request):
    if request.method == "POST":
        print('POST')
        form = TestModelForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('test_model')
    else:
        form = TestModelForm()
        data = TestModel.objects.all()
    context = {'form': form, 'data':data}
    return render(request, 'jdatester/home.html', context)


def test_model_edit(request, pk):
    if request.method == "POST":
        item = TestModel.objects.get(pk=pk)
        form = TestModelForm(request.POST or None, instance=item)

        if form.is_valid():
            form.save()
            return redirect('test_model')
    else:
        item = TestModel.objects.get(pk=pk)
        form = TestModelForm(instance=item)
        data = TestModel.objects.all()

    context = {'form': form, 'data':data}
    return render(request, 'jdatester/home.html', context)



#form = BalanceSheetForm(request.POST or None, instance=item)
def test_model_res(request):
    data = TestModel.objects.all()
    context ={'data':data}
    return render(request, 'jdatester/home.html', context)


def jdatester_ed(request):
    if request.method == "POST":
        print('POST')
        form = AuthorForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f" successfully saved ")
            return redirect('jdatester_ed')
        else:
            messages.error(request, form.errors)
    else:
        print("GET")
        form = AuthorForm()

    auth = Author.objects.all()
    context = {'form': form, 'auth':auth}
    return render(request, 'jdatester/ed.html', context)



def jdatester_book_formset(request):
    author =Author.objects.get(pk=4)
    book_formset = modelformset_factory(Book, fields=('title',))
    if request.method == 'POST':
        formset = book_formset(request.POST, queryset=Book.objects.filter(author_id=author.id))
        if formset.is_valid:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.author_id=author.id
                instance.save()
            messages.success(request, f"Successfully saved book from author {author.name}")
            return redirect('jdatester_book_formset')
        else:
            messages.error(request, formset.errors)
            return redirect('jdatester_book_formset')

    else:
        formset = book_formset(queryset=Book.objects.filter(author_id=author.id))

    context={'formset':formset}
    return render(request, 'jdatester/ed.html', context)

def jdatester_book_inline_formset(request):
    author =Author.objects.get(pk=4)
    book_inline_formset = inlineformset_factory(Author, Book, fields=('title',), extra=0)
    if request.method == 'POST':
        print("POST")
        formset = book_inline_formset(request.POST, instance=author)
        #formset = book_inline_formset(request.POST, request.FILES, instance=author)
        if formset.is_valid:
            formset.save()
            messages.success(request, f"Successfully saved book from author {author.name}")
            return redirect('jdatester_book_formset')
        else:
            messages.error(request, formset.errors)
            return redirect('jdatester_book_formset')

    else:
        print("GET")
        formset = book_inline_formset(instance=author)

    context={'formset':formset}
    return render(request, 'jdatester/ed.html', context)



#///////////////////////////////////////// jdatester_bal /////////////////////////

def jdatester_bal_dash(request):
    if request.method == "POST":
        form = DashForm(request.POST)

        if form.is_valid():
            company = form.cleaned_data['company']
            pub_period = form.cleaned_data['pub_period']

            entry_date = jdatester_publication_date(pub_period)
            #form.save()
            print(f"{company} - {entry_date}")
            messages.success(request, f" successfully saved ")
            return redirect('jdatester_bal', company, entry_date)
        else:
            pass
            #messages.error(request, form.errors)
    else:
        form = DashForm()

    context = {'form': form}
    return render(request, 'jdatester/jdatester_bal_dash.html', context)



def jdatester_bal(request, company, entry_date):
    company=jdatesterCompanyModel.objects.get(name=company)
    entry_date = publication_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()
    lines = jdatesterLineModel.objects.all()

    link_data = jdatesterLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)
    #link_data = jdatesterLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
    bal_data = jdatesterBalanceSheetModel.objects.filter(company_id=company.id, entry_date=entry_date)


    if request.method == "POST":
        print("POST")
        if link_data.count() > 0: # existing balance sheet
            item = jdatesterLinkModel.objects.get(pk=link_data[0].id)
            form = BalanceSheetForm(request.POST, instance=item)
        else: # new balance sheet
            form = BalanceSheetForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            for i in lines:
                instance.company_id = company.id
                instance.entry_date=entry_date
                instance.save()

            if bal_data.count() > 0:
                print(f"278 bal exists")
                # In existing balance sheet del item associated with company and entry_date
                bal_data.delete()
                # then Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = jdatesterLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_bal_link_data(lines, link_data, jdatesterBalanceSheetModel)
                #jdatesterBalanceSheetModel.objects.create(company_id=link_data.company.id, lbl_id=6, entry_date=link_data.entry_date, brut=link_data.brut_1)
                #jdatesterBalanceSheetModel.objects.create(company_id=link_data.company.id, lbl_id=7, entry_date=link_data.entry_date, brut=link_data.brut_2)

            else:
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = jdatesterLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_bal_link_data(lines, link_data, jdatesterBalanceSheetModel)
                #jdatesterBalanceSheetModel.objects.create(company_id=link_data.company.id, lbl_id=6, entry_date=link_data.entry_date, brut=link_data.brut_1)
                #jdatesterBalanceSheetModel.objects.create(company_id=link_data.company.id, lbl_id=7, entry_date=link_data.entry_date, brut=link_data.brut_2)

            messages.success(request, f" successfully saved ")
            return redirect('jdatester_bal', company, entry_date)
        else:
            messages.error(request, form.errors)
    else:
        print("GET")
        #1) Check if company and entry date exist in the link table
        link_data = jdatesterLinkModel.objects.filter(company_id=company.id, entry_date=entry_date)

        if link_data.count() > 0:
            item = jdatesterLinkModel.objects.get(pk=link_data[0].id)
            form = BalanceSheetForm(instance=item)
        else:
            form = BalanceSheetForm()

    link = jdatesterLinkModel.objects.all()
    bal  = jdatesterBalanceSheetModel.objects.all()


    context = {'form': form, 'bal':bal, 'lines':lines,'link':link}
    return render(request, 'jdatester/jdatester_bal.html', context)


#/////////////////////////////// export_data ///////////////////////////////////
def jdatester_export_data(request):
    if request.method == 'POST':
        # Get selected option from form
        file_format = request.POST['file-format']
        employee_resource = EmployeeResource()
        dataset = employee_resource.export()
        if file_format == 'CSV':
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'
            return response
        elif file_format == 'JSON':
            response = HttpResponse(dataset.json, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="exported_data.json"'
            return response
        elif file_format == 'XLS (Excel)':
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="exported_data.xls"'
            return response

    return render(request, 'jdatester/export.html')

#/////////////////////////////// import_data ///////////////////////////////////
def jdatester_import_data(request):
    print("356: Calling import_data")

    if request.method == 'POST':
        print("349: Post")
        #file_format = request.POST['file-format']
        new_employees = request.FILES['importData']
        print(type(new_employees))

        #df = pd.read_excel() (new_employees)
        #print(f"368: {df}")
        df = pd.DataFrame(data=new_employees).T
        print(f"371: {df}")

        employee_resource = EmployeeResource()
        dataset = Dataset()

        #new_employees = request.FILES['importData']
        #print(f"364: file_format: {file_format} ")
        imported_data = dataset.load(new_employees.read())
        print(f"372: dataset: {dataset} ")

        result = employee_resource.import_data(dataset, dry_run=True) # Test the data import
        print(f"368: {result} \n- result {result.has_errors()}")

        if not result.has_errors():
             employee_resource.import_data(dataset, dry_run=False) # Actually import now
             print(f"372: {result}")
        #
        # if file_format == 'XLSX':
        #     pass
        #     #imported_data = dataset.load(new_employees.read(), format='xlsx')
        #     #result = employee_resource.import_data(dataset, dry_run=True)
        #     #print("359 file format is xlxs")
        #     #print(f"359:{result.has_errors()}")
        #
        # if file_format == 'CSV':
        #     imported_data = dataset.load(new_employees.read().decode('utf-8'),format='csv')
        #     result = employee_resource.import_data(dataset, dry_run=True)
        #
        # elif file_format == 'JSON':
        #     imported_data = dataset.load(new_employees.read().decode('utf-8'),format='json')
        #     # Testing data import
        #     result = employee_resource.import_data(dataset, dry_run=True)
        #
        # else:
        #     print("unk format")
        # #if not result.has_errors():
        # #    # Import now
        # #    employee_resource.import_data(dataset, dry_run=False)
        #
        # #if result.has_validation_errors():
        # #    print("res")
        #
        # #else:
        #     #messages.error(request, result.base_errors)
        #     #print(result.base_errors)
        # #    print(f"368: result: {result} \n- {result.row_errors()} \nhas Error:{result.has_errors()}")
    emp_count = Employee.objects.all().count()
    context ={'emp_count':emp_count}
    return render(request, 'jdatester/import.html', context)

#///////////////////////////// jdatester_load_xls //////////////////////
from .forms import UploadExcelForm
from .models import UploadExcelModel

def jdatester_load_xls(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            wb = xlrd.open_workbook(filename=None, file_contents=request.FILES['excel'].read())  # The key point is here
            table = wb.sheets()[0]
            nbr_rows = table.nrows
            nbr_cols = table.ncols

            for i in range(1, nbr_rows):
                col = table.row_values(i)
                print (f"{col[1]}-{col[3]}-{col[4]}")
                UploadExcelModel.objects.create(last_name=col[1], location=col[4])

            return  redirect('jdatester_load_xls')

        #context={}#'nbr_rows':nbr_rows, 'nbr_cols':nbr_cols, 'cols':col}
        #return render(request, 'jdatester/load_xls.html', context)

    else:
        form = UploadExcelForm()

    data = UploadExcelModel.objects.all()
    context={'form':form, 'data':data}
    return render(request, 'jdatester/load_xls.html', context)


# #//////////////////////////// jdatester_index /////////////////////
# from .forms import IndexForm
# # from .models import IndexPriceModel, SecurityModel, SecurityPriceModel
# import xlrd
# from datetime import datetime
# from django.utils import timezone
# import pytz
#
# import pandas as pd

# def jdatester_index(request):
#     if request.method == 'POST':
#         form = IndexForm(request.POST, request.FILES)
#         if form.is_valid():
#             wb = xlrd.open_workbook(filename=None, file_contents=request.FILES['excel'].read())  # The key point is here
#             sheet = wb.sheets()[0]
#             nbr_rows = sheet.nrows
#             nbr_cols = sheet.ncols
#
#             # sheet = wb.sheet_by_index(0)
#             # date_cell = sheet.cell(3, 1)
#             # dt =xlrd.xldate_as_tuple(date_cell.value, wb.datemode)
#             # print(f"471: dt: {dt} |  {dt[0]}-{dt[1]}-{dt[2]} {dt[3]}:{dt[4]}:{dt[5]}")
#             # print(str(dt))
#             # dt_obj = datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5])
#             # date_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
#             # print(date_str)
#
#             print(f"nbr_rows: {nbr_rows} - nbr_cols: {nbr_cols}")
#             #col_0_val=sheet.row_values(0, start_colx=0, end_colx=1)
#             col_0_val =sheet.cell(0,0).value
#             if col_0_val == "Liste des cours": # check if it's the right file
#                 # get file datetime
#                 date_cell = sheet.cell(3, 1)
#                 dt = xlrd.xldate_as_tuple(date_cell.value, wb.datemode)
#                 dt_obj = datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], tzinfo=pytz.UTC)
#
#                 for idx, i in enumerate(range(19, nbr_rows), 0):
#                     cols = sheet.row_values(i)
#                     print(f"idx:{idx} - i: {i} - cols[0]: {cols[0]} - cols[7]: {type(cols[7])}")
#                 #date_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
#                 #print("489")
#                 #print(datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], tzinfo=pytz.UTC))
#                 #print(dt)
#                 print(f"487: {dt_obj}")
#                 #check if datetime exists in DB/ Opt1: delete and reload Opt2:
#                 if 1==2: #IndexPriceModel.objects.filter(index_date = dt_obj):
#                     messages.info(request, f"market data as of {dt_obj} already loaded")
#                 else:
#                     # get index info save it to DB
#                     for i in range(6, 15): # index price info in spreadsheet starting from row 6 to row 15th
#                         cols = sheet.row_values(i)
#                         #print (f"489: {cols[0]}-{cols[1]}")
#                         #py_date = datetime(cols[2])
#                         #print(f"py_date: {py_date}")
#                         #IndexPriceModel.objects.create(index_date=dt_obj, index=cols[0], value=cols[1])
#
#                     #get security info
#                     for i in range(19, nbr_rows): # security info
#                         cols =sheet.row_values(i)
#                         #print(f"503: {cols[0]} - {cols[1]} - {cols[2]}")
#                         #SecurityModel.objects.create(ticker=cols[0], isin=cols[1], name=cols[2])
#
#                     #get SecurityPriceModel info
#                     for idx, i in enumerate(range(19, nbr_rows), 0):
#
#                         cols = sheet.row_values(i)
#                         #print(f"519: cols type {type(cols)}")
#
#                         if isinstance(cols[7], str):
#                             cols[7]=None
#                         if isinstance(cols[10], str):
#                             cols[10]=None
#                         if isinstance(cols[11], str):
#                             cols[11]=None
#                         if isinstance(cols[13], str):
#                             cols[13]=None
#                         if isinstance(cols[14], str):
#                             cols[14]=None
#                         if isinstance(cols[15], str):
#                             cols[15]=None
#                         if isinstance(cols[16], str):
#                             cols[16]=None
#                         if isinstance(cols[17], str):
#                             cols[17]=None
#                         if isinstance(cols[18], str):
#                             cols[18]=None
#                         if isinstance(cols[19], str):
#                             cols[19]=None
#                         #print(f"idx:{idx} - i: {i} - cols[0]: {cols[0]} - cols[7]:{cols[7]} type: {type(cols[7])}")
#                         # sec_id =SecurityModel.objects.all()[idx].id
#                         # SecurityPriceModel.objects.create(security_id=sec_id, security_date=dt_obj, avg_price=cols[7], open=cols[10], close=cols[11], high=cols[13], low=cols[14], ask=cols[15], bid=cols[16], trans_total=cols[17], volume=cols[18], trans_value=cols[19])
#                         #spm =SecurityPriceModel.objects.create() #security=IndexPriceModel.objects.all(),  security_date=date_str)#, avg_price=cols[7], open=cols[10], close=cols[11], high=cols[13], low=cols[14], ask=cols[15], bid=cols[16], trans_total=cols[17], volume=cols[18], trans_value=cols[19])
#                         #spm.security = SecurityModel.objects.get(pk=cols[0])
#                         #spm.security_date = date_str
#                         #spm.save()
#                         #print(f"509: {cols[7]} - {cols[10]} - {cols[11]} - {cols[13]} - {cols[14]} - {cols[15]} - {cols[16]} - {cols[17]} - {cols[18]} - {cols[19]}")
#             #else:
#                 #print(f"469: {str(col_0_val)} ")
#             #    messages.warning(request, f"Please make sure you loaded the right file with 'Liste des cours'")
#
#             #print(f"col_val: {col_0_val}")
#             #for i in range(1, nbr_rows):
#             #    col = table.row_values(i)
#             #    print (f"{col[1]}-{col[3]}-{col[4]}")
#                 #IndexPriceModel.objects.create(last_name=col[1], location=col[4])
#
#             return  redirect('jdatester_index')
#
#     else:
#         form = UploadExcelForm()
#
#     filterForm = SecurityFilterForm()

    # index = IndexPriceModel.objects.all()
    # security = SecurityModel.objects.all()
    # security_price = SecurityPriceModel.objects.all()

    # context={'form':form, 'filterForm':filterForm,'index':index, 'security':security, 'security_price':security_price}
    # return render(request, 'jdatester/jdatester_index.html', context)





# #/////////////////////// jdatester_sec_filter /////////////////////
# #@login_required
# def jdatester_sec_filter(request):
#     now = datetime.now()
#     if request.method == 'POST':
#
#         filterForm = SecurityFilterForm(request.POST)
#         if filterForm.is_valid():
#
#             security_date = filterForm.cleaned_data['security_date']
#             ticker = filterForm.cleaned_data['ticker']
#             index = filterForm.cleaned_data['index']
#
#             print(f"119://// security_date:{security_date} ticker:{ticker} index:{index} ")
#
#             # # build querystring conditions
#             if security_date!=None and ticker==None and index==None: # security_date only
#                  #max_index_dt = IndexPriceModel.objects.latest('security_date').index_date
#                  index = IndexPriceModel.objects.filter(index_date=security_date)
#                  #index = IndexPriceModel.objects.filter(index_date=security_date)
#                  #security = SecurityModel.objects.all()
#                  index = IndexPriceModel.objects.filter(security_date=security_date)
#                  security = SecurityModel.objects.all()
#                  security_price = SecurityPriceModel.filter(security_date=security_date)
#
#                  if index:
#                       messages.success(request, f"Found {index.count()} item(s) associated with all empty filters")
#
#                       context = {'filterForm': filterForm, 'index': index, 'security': security, 'security_price': security_price}
#                       return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)
#                  else:
#                       messages.warning(request,f"Could not find any items associated with {security_date} filter")
#             #
#         #else:
#         #    print("147 invalid form")
#         #    messages.error(request, filterForm.errors)
#         #    print(f"149 form.errors {filterForm.errors} ///////")
#         #    return  redirect('jdatester_index')
#
#     else:
#         filterForm =SecurityFilterForm()
#
#     index = IndexPriceModel.objects.all()
#     security = SecurityModel.objects.all()
#     security_price = SecurityPriceModel.objects.all()
#
#     context = {'filterForm': filterForm, 'index': index, 'security': security, 'security_price': security_price}
#     return render(request, 'jdatester/jdatester_index.html', context)
#
#

from django.contrib.auth.decorators import login_required

def blog_listing(request):
    blogs =  Blog.objects.all()
    context ={"blogs": blogs}

    return render(request, "jdatester/blog_listing.html", context)

def blog_view(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    context=  {"blog": blog}

    return render(request, "jdatester/blog_view.html", context)


def blog_see_request(request):
    text = f"""
        Some attributes of the HttpRequest object:

        scheme: {request.scheme}
        path:   {request.path}
        method: {request.method}
        GET:    {request.GET}
        user:   {request.user}
    """

    return HttpResponse(text, content_type="text/plain")


def blog_user_info(request):
    text = f"""
        Selected HttpRequest.user attributes:

        username:     {request.user.username}
        is_anonymous: {request.user.is_anonymous}
        is_staff:     {request.user.is_staff}
        is_superuser: {request.user.is_superuser}
        is_active:    {request.user.is_active}
    """

    return HttpResponse(text, content_type="text/plain")

@login_required
def blog_private_place(request):
    return HttpResponse("Shhh, members only!", content_type="text/plain")


from django.contrib.auth.decorators import user_passes_test

@login_required
@user_passes_test(lambda user: user.is_staff)
def blog_staff_place(request):
    return HttpResponse("Employees must wash hands", content_type="text/plain")
# a = Album(title="Divide", artist="Ed Sheeran", genre="Pop")
# a.save()

#queryset=Book.objects.filter(author_id=author.id