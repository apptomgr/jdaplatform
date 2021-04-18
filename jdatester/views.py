from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CourseForm, TestModelForm
from jdafinancialsapp.forms import FinancialStatementFactForm
from .models import Student, Book, Course, TestModel
from jdafinancialsapp.models import CompanyModel, FinancialStatementLineModel, FinancialStatementFactModel, FinancialStatementLineSequenceModel, FinancialStatementModel
from django.forms import modelformset_factory
from django.contrib import messages
from datetime import datetime
from .forms import AuthorForm, BalanceSheetForm, DashForm
from .models import Author, Book, jdatesterBalanceSheetModel, jdatesterCompanyModel, jdatesterLineModel, jdatesterLinkModel
from django.forms import modelformset_factory, inlineformset_factory
from django.db import IntegrityError
from jdafinancialsapp.utils import jdatester_publication_date, jdafinancialsapp_migrate_bal_link_data

def jdatester_home(request):
    form = CourseForm()

    context ={'form':form}
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
                jdafinancialsapp_migrate_link_data(lines, link_data, jdatesterBalanceSheetModel)
                #jdatesterBalanceSheetModel.objects.create(company_id=link_data.company.id, lbl_id=6, entry_date=link_data.entry_date, brut=link_data.brut_1)
                #jdatesterBalanceSheetModel.objects.create(company_id=link_data.company.id, lbl_id=7, entry_date=link_data.entry_date, brut=link_data.brut_2)

            else:
                # new balance sheet items (add try/catch block)
                # Read data from jdatesterLinkModel and insert it into jdatesterBalanceSheetModel
                link_data = jdatesterLinkModel.objects.get(company_id=company.id, entry_date=entry_date)
                jdafinancialsapp_migrate_link_data(lines, link_data, jdatesterBalanceSheetModel)
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




# a = Album(title="Divide", artist="Ed Sheeran", genre="Pop")
# a.save()